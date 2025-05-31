-- 文化資產統計組件清理和重新設定腳本
-- 此腳本先清理可能的部分數據，然後重新插入完整配置

-- 1. 清理可能存在的部分數據
DELETE FROM component_charts WHERE index = 'cultural_heritage_statistics';
DELETE FROM query_charts WHERE index = 'cultural_heritage_statistics';
DELETE FROM components WHERE index = 'cultural_heritage_statistics';

-- 2. 插入 components 表
INSERT INTO components (index, name) 
VALUES ('cultural_heritage_statistics', '文化資產行政區統計');

-- 3. 插入 query_charts 表 (台北市)
INSERT INTO query_charts (
    index, 
    city,
    query_type, 
    query_chart,
    time_from,
    time_to,
    update_freq,
    update_freq_unit,
    source,
    short_desc,
    long_desc,
    use_case,
    links,
    contributors,
    created_at,
    updated_at
) 
VALUES (
    'cultural_heritage_statistics',
    'taipei',
    'three_d',
    'SELECT district as x_axis, category as y_axis, sum(count) as data FROM cultural_heritage_statistics WHERE city = ''台北市'' AND data_time >= ''%s'' AND data_time <= ''%s'' GROUP BY district, category ORDER BY district, category',
    '2024-01-01',
    'now',
    1,
    'week',
    '台北市文化局',
    '台北市各行政區文化資產數量統計，依資產類型分類呈現',
    '本組件統計台北市各行政區內的文化資產總數及類型分布，包含古蹟、歷史建築、考古遺址、紀念建築等不同類型。透過縱向長條圖呈現各行政區的文化資產豐富程度，有助於了解台北市文化資產的地理分布特性。',
    '可用於文化政策規劃、觀光路線設計、文化資產保護優先序評估等用途',
    '{"https://iheritage.gov.taipei/data/api/designation/data"}',
    '{"文化局"}',
    NOW(),
    NOW()
);

-- 4. 插入 query_charts 表 (新北市)
INSERT INTO query_charts (
    index, 
    city,
    query_type, 
    query_chart,
    time_from,
    time_to,
    update_freq,
    update_freq_unit,
    source,
    short_desc,
    long_desc,
    use_case,
    links,
    contributors,
    created_at,
    updated_at
) 
VALUES (
    'cultural_heritage_statistics',
    'metrotaipei',
    'three_d',
    'SELECT district as x_axis, category as y_axis, sum(count) as data FROM cultural_heritage_statistics WHERE city = ''新北市'' AND data_time >= ''%s'' AND data_time <= ''%s'' GROUP BY district, category ORDER BY district, category',
    '2024-01-01',
    'now',
    1,
    'week',
    '新北市文化局',
    '新北市各行政區文化資產數量統計，依資產類型分類呈現',
    '本組件統計新北市各行政區內的文化資產總數及類型分布，包含古蹟、歷史建築等不同類型。透過縱向長條圖呈現各行政區的文化資產豐富程度，有助於了解新北市文化資產的地理分布特性。',
    '可用於文化政策規劃、觀光路線設計、文化資產保護優先序評估等用途',
    '{"https://data.ntpc.gov.tw/api/datasets/d8eb898f-6c59-4689-9191-48dbbef16606/csv"}',
    '{"文化局"}',
    NOW(),
    NOW()
);

-- 5. 插入 component_charts 表
INSERT INTO component_charts (index, color, types, unit) 
VALUES (
    'cultural_heritage_statistics',
    '{"#5a9cf8", "#7dd3fc", "#06b6d4", "#0891b2", "#0e7490", "#155e75"}',
    '{"ColumnChart"}',
    '處'
);

-- 查詢驗證插入結果
SELECT 'Components cleaned and inserted successfully' as status;
SELECT c.id, c.index, c.name FROM components c WHERE c.index = 'cultural_heritage_statistics';
SELECT qc.index, qc.city, qc.query_type, qc.created_at, qc.updated_at FROM query_charts qc WHERE qc.index = 'cultural_heritage_statistics';
SELECT cc.index, cc.unit FROM component_charts cc WHERE cc.index = 'cultural_heritage_statistics'; 