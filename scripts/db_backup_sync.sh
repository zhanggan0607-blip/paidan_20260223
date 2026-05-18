#!/bin/bash
# 数据库增量同步脚本
# 每天从生产RDS增量同步变更数据到测试数据库
# 策略：基于updated_at时间戳的增量同步 + 每周日全量同步
# 源: pgm-uf6cml154nbjz51y.pg.rds.aliyuncs.com:5432/tq (生产RDS)
# 目标: 101.35.134.211:5432/tq (测试数据库)
# 容错：自动重试(3次)、网络检测、单表失败不影响其他表

MAX_RETRIES=3
RETRY_DELAY=30
CONNECT_TIMEOUT=10

SOURCE_HOST='pgm-uf6cml154nbjz51y.pg.rds.aliyuncs.com'
SOURCE_PORT='5432'
SOURCE_DB='tq'
SOURCE_USER='postgres'

TARGET_HOST='101.35.134.211'
TARGET_PORT='5432'
TARGET_DB='tq'
TARGET_USER='postgres'

PG_DUMP17='/usr/lib/postgresql/17/bin/pg_dump'
PSQL17='/usr/lib/postgresql/17/bin/psql'

BACKUP_DIR='/opt/sstcp/backups'
LOG_FILE='/opt/sstcp/logs/db_backup_sync.log'
LAST_SYNC_FILE='/opt/sstcp/backups/.last_sync_time'
RETAIN_DAYS=7

TABLES_WITH_UPDATED_AT=(
    'customer'
    'customer_contact'
    'dictionary'
    'inspection_item'
    'maintenance_log'
    'maintenance_plan'
    'operation_type'
    'periodic_inspection'
    'periodic_inspection_record'
    'personnel'
    'project_info'
    'repair_tools_issue'
    'repair_tools_stock'
    'spare_parts_stock'
    'spare_parts_usage'
    'spot_work'
    'spot_work_worker'
    'temporary_repair'
    'uploaded_file'
    'user_dashboard_config'
    'weekly_report'
    'work_plan'
)

TABLES_NO_UPDATED_AT=(
    'online_users'
    'repair_tools_inbound'
    'spare_parts_inbound'
    'work_order_operation_log'
)

FAILED_TABLES=()

mkdir -p "$BACKUP_DIR"
mkdir -p "$(dirname "$LOG_FILE")"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_warn() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [警告] $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [错误] $1" | tee -a "$LOG_FILE"
}

check_db_connection() {
    local host="$1" port="$2" user="$3" db="$4" label="$5"
    local attempt=1
    while [ $attempt -le $MAX_RETRIES ]; do
        if PGPASSWORD=$(eval echo "\$PGPASS_$(echo $label | tr '[:lower:]' '[:upper:]')") \
            $PSQL17 -h "$host" -p "$port" -U "$user" -d "$db" \
            -c "SELECT 1;" -c "SET statement_timeout = '${CONNECT_TIMEOUT}s';" \
            >> /dev/null 2>&1; then
            log "${label}数据库连接正常"
            return 0
        fi
        log_warn "${label}数据库连接失败(第${attempt}/${MAX_RETRIES}次), ${RETRY_DELAY}秒后重试..."
        sleep $RETRY_DELAY
        attempt=$((attempt + 1))
    done
    log_error "${label}数据库连接失败, 已重试${MAX_RETRIES}次"
    return 1
}

retry_cmd() {
    local desc="$1"
    shift
    local attempt=1
    while [ $attempt -le $MAX_RETRIES ]; do
        if "$@" >> "$LOG_FILE" 2>&1; then
            return 0
        fi
        log_warn "${desc}失败(第${attempt}/${MAX_RETRIES}次), ${RETRY_DELAY}秒后重试..."
        sleep $RETRY_DELAY
        attempt=$((attempt + 1))
    done
    log_error "${desc}失败, 已重试${MAX_RETRIES}次"
    return 1
}

retry_cmd_stdout() {
    local desc="$1"
    local outfile="$2"
    shift 2
    local attempt=1
    while [ $attempt -le $MAX_RETRIES ]; do
        if "$@" > "$outfile" 2>> "$LOG_FILE"; then
            return 0
        fi
        log_warn "${desc}失败(第${attempt}/${MAX_RETRIES}次), ${RETRY_DELAY}秒后重试..."
        rm -f "$outfile"
        sleep $RETRY_DELAY
        attempt=$((attempt + 1))
    done
    rm -f "$outfile"
    log_error "${desc}失败, 已重试${MAX_RETRIES}次"
    return 1
}

SOURCE_PSQL="$PSQL17 -h $SOURCE_HOST -p $SOURCE_PORT -U $SOURCE_USER -d $SOURCE_DB"
TARGET_PSQL="$PSQL17 -h $TARGET_HOST -p $TARGET_PORT -U $TARGET_USER -d $TARGET_DB"

log "========== 开始同步前检查 =========="
if ! check_db_connection "$SOURCE_HOST" "$SOURCE_PORT" "$SOURCE_USER" "$SOURCE_DB" "源"; then
    log_error "源数据库不可达, 同步终止"
    exit 1
fi
if ! check_db_connection "$TARGET_HOST" "$TARGET_PORT" "$TARGET_USER" "$TARGET_DB" "目标"; then
    log_error "目标数据库不可达, 同步终止"
    exit 1
fi

DAY_OF_WEEK=$(date +%u)

if [ "$DAY_OF_WEEK" -eq 7 ]; then
    log "========== 开始每周全量同步 =========="
    log "今天是周日，执行全量同步"

    TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
    DUMP_FILE="${BACKUP_DIR}/${SOURCE_DB}_full_${TIMESTAMP}.sql.gz"

    log "步骤1: 从RDS全量导出..."
    if ! retry_cmd "全量导出" $PG_DUMP17 \
        -h "$SOURCE_HOST" \
        -p "$SOURCE_PORT" \
        -U "$SOURCE_USER" \
        -d "$SOURCE_DB" \
        --no-owner \
        --no-acl \
        --clean \
        --if-exists \
        bash -c 'gzip > "$0"' "$DUMP_FILE"; then
        log_error "全量导出失败, 同步终止"
        exit 1
    fi

    DUMP_SIZE=$(du -h "$DUMP_FILE" | cut -f1)
    log "导出完成, 文件: $DUMP_FILE, 大小: $DUMP_SIZE"

    log "步骤2: 断开目标数据库活动连接..."
    $TARGET_PSQL \
        -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='${TARGET_DB}' AND pid <> pg_backend_pid();" \
        >> "$LOG_FILE" 2>&1 || true

    log "步骤3: 全量导入到测试数据库..."
    if ! retry_cmd "全量导入" bash -c 'gunzip -c "$0" | '"$PSQL17"' -h "'"$TARGET_HOST"'" -p "'"$TARGET_PORT"'" -U "'"$TARGET_USER"'" -d "'"$TARGET_DB"'" -v ON_ERROR_STOP=0' "$DUMP_FILE"; then
        log_error "全量导入失败"
        exit 1
    fi

    date -u '+%Y-%m-%dT%H:%M:%S' > "$LAST_SYNC_FILE"
    log "全量同步完成, 已更新同步时间戳"
else
    log "========== 开始增量同步 =========="
    log "源: ${SOURCE_HOST}:${SOURCE_PORT}/${SOURCE_DB}"
    log "目标: ${TARGET_HOST}:${TARGET_PORT}/${TARGET_DB}"

    if [ -f "$LAST_SYNC_FILE" ]; then
        LAST_SYNC=$(cat "$LAST_SYNC_FILE")
        log "上次同步时间: $LAST_SYNC"
    else
        LAST_SYNC=$(date -u -d '1 day ago' '+%Y-%m-%dT%H:%M:%S')
        log "无同步记录, 使用1天前作为起点: $LAST_SYNC"
    fi

    TOTAL_UPDATES=0

    log "步骤1: 增量同步有updated_at字段的表..."
    for TABLE in "${TABLES_WITH_UPDATED_AT[@]}"; do
        log "  同步表: $TABLE"

        CHANGED_COUNT=$($SOURCE_PSQL -t -c \
            "SELECT count(*) FROM ${TABLE} WHERE updated_at >= '${LAST_SYNC}' OR created_at >= '${LAST_SYNC}';" \
            2>> "$LOG_FILE" | tr -d ' ') || {
            log_warn "  查询${TABLE}变更数失败, 跳过该表"
            FAILED_TABLES+=("$TABLE")
            continue
        }

        if [ "$CHANGED_COUNT" -eq 0 ] 2>/dev/null; then
            log "    无变更, 跳过"
            continue
        fi

        log "    发现 ${CHANGED_COUNT} 条变更记录"

        TEMP_FILE="${BACKUP_DIR}/incr_${TABLE}_$$.sql"

        if retry_cmd_stdout "导出${TABLE}" "$TEMP_FILE" $PG_DUMP17 \
            -h "$SOURCE_HOST" \
            -p "$SOURCE_PORT" \
            -U "$SOURCE_USER" \
            -d "$SOURCE_DB" \
            -t "public.${TABLE}" \
            --data-only \
            --no-owner \
            --no-acl \
            --column-inserts; then

            if [ -s "$TEMP_FILE" ]; then
                if retry_cmd "导入${TABLE}" $TARGET_PSQL -v ON_ERROR_STOP=0 < "$TEMP_FILE"; then
                    TOTAL_UPDATES=$((TOTAL_UPDATES + CHANGED_COUNT))
                    log "    同步完成"
                else
                    log_warn "  导入${TABLE}失败, 记录到失败列表"
                    FAILED_TABLES+=("$TABLE")
                fi
            else
                log "    导出文件为空, 跳过"
            fi
        else
            log_warn "  导出${TABLE}失败, 记录到失败列表"
            FAILED_TABLES+=("$TABLE")
        fi

        rm -f "$TEMP_FILE"
    done

    log "步骤2: 全量刷新无updated_at字段的表..."
    for TABLE in "${TABLES_NO_UPDATED_AT[@]}"; do
        log "  刷新表: $TABLE"

        TEMP_FILE="${BACKUP_DIR}/refresh_${TABLE}_$$.sql"

        if retry_cmd_stdout "导出${TABLE}" "$TEMP_FILE" $PG_DUMP17 \
            -h "$SOURCE_HOST" \
            -p "$SOURCE_PORT" \
            -U "$SOURCE_USER" \
            -d "$SOURCE_DB" \
            -t "public.${TABLE}" \
            --no-owner \
            --no-acl \
            --clean \
            --if-exists; then

            if [ -s "$TEMP_FILE" ]; then
                if retry_cmd "导入${TABLE}" $TARGET_PSQL -v ON_ERROR_STOP=0 < "$TEMP_FILE"; then
                    log "    刷新完成"
                else
                    log_warn "  导入${TABLE}失败, 记录到失败列表"
                    FAILED_TABLES+=("$TABLE")
                fi
            else
                log "    导出文件为空, 跳过"
            fi
        else
            log_warn "  导出${TABLE}失败, 记录到失败列表"
            FAILED_TABLES+=("$TABLE")
        fi

        rm -f "$TEMP_FILE"
    done

    if [ ${#FAILED_TABLES[@]} -eq 0 ]; then
        date -u '+%Y-%m-%dT%H:%M:%S' > "$LAST_SYNC_FILE"
        log "增量同步完成, 增量变更: ${TOTAL_UPDATES} 条"
    else
        log_warn "以下表同步失败, 不更新同步时间戳(下次将重试): ${FAILED_TABLES[*]}"
        log "增量同步部分完成, 成功变更: ${TOTAL_UPDATES} 条, 失败表: ${#FAILED_TABLES[@]} 个"
    fi
fi

log "步骤3: 验证同步结果..."
TABLE_COUNT=$($TARGET_PSQL -t -c \
    "SELECT count(*) FROM information_schema.tables WHERE table_schema='public';" \
    2>> "$LOG_FILE" | tr -d ' ') || TABLE_COUNT="查询失败"
log "测试数据库public表数量: $TABLE_COUNT"

log "步骤4: 清理${RETAIN_DAYS}天前的备份文件..."
find "$BACKUP_DIR" -name "${SOURCE_DB}_*.sql.gz" -mtime +${RETAIN_DAYS} -delete 2>/dev/null || true
find "$BACKUP_DIR" -name "incr_*.sql" -mtime +1 -delete 2>/dev/null || true
find "$BACKUP_DIR" -name "refresh_*.sql" -mtime +1 -delete 2>/dev/null || true
REMAINING=$(ls -1 "${BACKUP_DIR}"/${SOURCE_DB}_*.sql.gz 2>/dev/null | wc -l)
log "保留备份文件数: $REMAINING"

if [ ${#FAILED_TABLES[@]} -gt 0 ]; then
    log "========== 同步结束(有失败表) =========="
    exit 1
else
    log "========== 同步结束 =========="
fi
