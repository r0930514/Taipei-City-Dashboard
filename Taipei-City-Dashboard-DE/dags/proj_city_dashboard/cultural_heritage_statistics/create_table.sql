-- 建立文化資產統計數據表
-- 此表用於儲存台北市和新北市的文化資產統計數據

-- 主要數據表
CREATE TABLE IF NOT EXISTS cultural_heritage_statistics (
    id SERIAL PRIMARY KEY,
    city VARCHAR(50) NOT NULL,
    district VARCHAR(50) NOT NULL,
    category VARCHAR(100) NOT NULL,
    count INTEGER NOT NULL DEFAULT 0,
    data_time TIMESTAMP WITH TIME ZONE NOT NULL,
    update_time TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- 歷史數據表
CREATE TABLE IF NOT EXISTS cultural_heritage_statistics_history (
    id SERIAL PRIMARY KEY,
    city VARCHAR(50) NOT NULL,
    district VARCHAR(50) NOT NULL,
    category VARCHAR(100) NOT NULL,
    count INTEGER NOT NULL DEFAULT 0,
    data_time TIMESTAMP WITH TIME ZONE NOT NULL,
    update_time TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- 建立索引以提升查詢效能
CREATE INDEX IF NOT EXISTS idx_cultural_heritage_city_district 
ON cultural_heritage_statistics(city, district);

CREATE INDEX IF NOT EXISTS idx_cultural_heritage_category 
ON cultural_heritage_statistics(category);

CREATE INDEX IF NOT EXISTS idx_cultural_heritage_data_time 
ON cultural_heritage_statistics(data_time);

CREATE INDEX IF NOT EXISTS idx_cultural_heritage_history_city_district 
ON cultural_heritage_statistics_history(city, district);

CREATE INDEX IF NOT EXISTS idx_cultural_heritage_history_category 
ON cultural_heritage_statistics_history(category);

CREATE INDEX IF NOT EXISTS idx_cultural_heritage_history_data_time 
ON cultural_heritage_statistics_history(data_time);

-- 建立註解
COMMENT ON TABLE cultural_heritage_statistics IS '台北市及新北市文化資產統計數據';
COMMENT ON COLUMN cultural_heritage_statistics.city IS '城市名稱（台北市或新北市）';
COMMENT ON COLUMN cultural_heritage_statistics.district IS '行政區名稱';
COMMENT ON COLUMN cultural_heritage_statistics.category IS '文化資產類別';
COMMENT ON COLUMN cultural_heritage_statistics.count IS '該行政區該類別的文化資產數量';
COMMENT ON COLUMN cultural_heritage_statistics.data_time IS '數據產生時間';
COMMENT ON COLUMN cultural_heritage_statistics.update_time IS '數據更新時間';

COMMENT ON TABLE cultural_heritage_statistics_history IS '台北市及新北市文化資產統計歷史數據';

-- 插入測試數據（可選）
INSERT INTO cultural_heritage_statistics (city, district, category, count, data_time, update_time) VALUES
('台北市', '中正區', '古蹟', 15, NOW(), NOW()),
('台北市', '中正區', '歷史建築', 8, NOW(), NOW()),
('台北市', '大安區', '古蹟', 5, NOW(), NOW()),
('台北市', '大安區', '歷史建築', 12, NOW(), NOW()),
('新北市', '淡水區', '古蹟', 10, NOW(), NOW()),
('新北市', '淡水區', '歷史建築', 6, NOW(), NOW()),
('新北市', '板橋區', '古蹟', 3, NOW(), NOW()),
('新北市', '板橋區', '歷史建築', 4, NOW(), NOW())
ON CONFLICT DO NOTHING;

-- 驗證表格建立成功
SELECT 'Tables created successfully' as status;
SELECT COUNT(*) as sample_data_count FROM cultural_heritage_statistics; 