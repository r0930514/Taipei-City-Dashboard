# 文化資產行政區統計組件

## 概述
此組件提供台北市及新北市各行政區文化資產數量的統計分析，支援按資產類型分類的縱向長條圖視覺化呈現。

## 功能特色
- 🏛️ **多城市支援**：同時支援台北市與新北市數據
- 📊 **類型分類**：按古蹟、歷史建築等類型分類統計
- 🗺️ **行政區分布**：展示各行政區文化資產豐富程度
- ⏰ **自動更新**：每週自動更新數據

## 數據來源
- **台北市**：[台北市文化資產API](https://iheritage.gov.taipei/data/api/designation/data)
- **新北市**：[新北市開放數據平台](https://data.ntpc.gov.tw/api/datasets/d8eb898f-6c59-4689-9191-48dbbef16606/csv)

## 技術規格

### 數據處理流程
1. **擷取**：從API和CSV來源獲取原始文化資產數據
2. **轉換**：解析地址提取行政區資訊，標準化資產類別
3. **統計**：按城市、行政區、類別彙總數量
4. **載入**：存入PostgreSQL數據庫

### 資料庫結構
```sql
cultural_heritage_statistics (
    id SERIAL PRIMARY KEY,
    city VARCHAR(50) NOT NULL,        -- 城市名稱
    district VARCHAR(50) NOT NULL,    -- 行政區名稱  
    category VARCHAR(100) NOT NULL,   -- 文化資產類別
    count INTEGER NOT NULL,           -- 數量
    data_time TIMESTAMP WITH TIME ZONE,
    update_time TIMESTAMP WITH TIME ZONE
)
```

### API端點
- **圖表數據**：`/api/v1/components/{id}/chart?city=taipei`
- **圖表數據**：`/api/v1/components/{id}/chart?city=metrotaipei`

### 前端組件
- **圖表類型**：ColumnChart（縱向長條圖）
- **數據類型**：three_d（三維數據）
- **互動功能**：支援圖表點擊篩選

## 部署指南

### 1. 資料庫初始化
```bash
# 建立數據表
psql -d dashboard_db -f create_table.sql

# 插入組件配置
psql -d dashboard_db -f setup_component.sql
```

### 2. Airflow DAG部署
```bash
# 將組件資料夾複製到Airflow DAGs目錄
cp -r cultural_heritage_statistics/ /opt/airflow/dags/proj_city_dashboard/

# 重啟Airflow
docker-compose restart airflow-webserver airflow-scheduler
```

### 3. 手動執行測試
```bash
# 在Airflow Web UI中觸發執行
# DAG ID: cultural_heritage_statistics
```

## 配置參數

| 參數 | 值 | 說明 |
|------|------|------|
| DAG ID | `cultural_heritage_statistics` | Airflow作業識別碼 |
| 更新頻率 | `0 2 * * 1` | 每週一凌晨2:00執行 |
| 數據保留 | `current+history` | 保留當前及歷史數據 |
| 圖表類型 | `ColumnChart` | 縱向長條圖 |
| 數據類型 | `three_d` | 三維數據格式 |

## 數據格式範例

### 台北市數據格式
```json
{
  "個案名稱": "大安十二甲東門住宅利用信用購買組合房舍",
  "資產類別": "歷史建築",
  "資產種類": "宅第",
  "所屬主管機關": "臺北市政府",
  "所在地理區域": "臺北市大安區",
  "現況地址": ["大安區永康街31巷11號"]
}
```

### 新北市數據格式
```csv
name,affection,category,rank,date,address
淡水紅毛城,古蹟,衙署,國定,72.12.28,淡水區中正路28巷1號
```

### 輸出數據格式
```json
{
  "data": [
    {
      "name": "古蹟",
      "data": [15, 8, 5, 12, 10, 6, 3, 4]
    },
    {
      "name": "歷史建築", 
      "data": [8, 12, 5, 15, 6, 10, 4, 7]
    }
  ],
  "categories": ["中正區", "大安區", "信義區", "松山區", "淡水區", "板橋區", "新莊區", "三重區"]
}
```

## 維護說明

### 監控項目
- 數據來源API可用性
- 地址解析準確度
- 數據更新時效性
- 圖表渲染效能

### 常見問題
1. **地址解析失敗**：檢查正則表達式模式是否涵蓋新的地址格式
2. **數據缺失**：確認API端點可用性及網路連線
3. **類別異常**：檢查資產類別標準化邏輯

## 授權
本組件遵循專案主要授權條款。數據來源請遵守各自開放數據使用規範。 