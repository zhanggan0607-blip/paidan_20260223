#!/bin/bash
# 组织恢复的图片文件

SRC_DIR="/tmp/recovered_images/var/lib/containers/storage/overlay"
DST_DIR="/tmp/organized_uploads"

mkdir -p "$DST_DIR"

# 遍历所有overlay层
for layer in "$SRC_DIR"/*; do
    if [ -d "$layer" ]; then
        # 查找uploads目录
        for uploads_dir in "$layer"/diff/app/app/uploads/*; do
            if [ -d "$uploads_dir" ]; then
                date_dir=$(basename "$uploads_dir")
                mkdir -p "$DST_DIR/$date_dir"
                cp -r "$uploads_dir"/* "$DST_DIR/$date_dir/" 2>/dev/null
            fi
        done
    fi
done

echo "组织完成"
find "$DST_DIR" -type f | wc -l
