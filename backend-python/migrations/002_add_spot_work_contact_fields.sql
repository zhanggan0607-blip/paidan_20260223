-- 数据库迁移脚本：为 spot_work 表添加客户联系人和联系电话字段
-- 执行日期：2026-02-19
-- 说明：添加 client_contact 和 client_contact_info 字段

-- ============================================
-- 1. 添加 client_contact 字段
-- ============================================
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'spot_work' AND column_name = 'client_contact') THEN
        ALTER TABLE spot_work ADD COLUMN client_contact VARCHAR(100);
        COMMENT ON COLUMN spot_work.client_contact IS '客户联系人';
    END IF;
END $$;

-- ============================================
-- 2. 添加 client_contact_info 字段
-- ============================================
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'spot_work' AND column_name = 'client_contact_info') THEN
        ALTER TABLE spot_work ADD COLUMN client_contact_info VARCHAR(50);
        COMMENT ON COLUMN spot_work.client_contact_info IS '客户联系电话';
    END IF;
END $$;

-- ============================================
-- 完成
-- ============================================
-- 迁移完成，请验证数据一致性
