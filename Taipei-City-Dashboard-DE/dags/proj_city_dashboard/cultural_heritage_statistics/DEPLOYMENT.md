# 文化資產統計組件部署指南

## 📋 部署前檢查清單

### 系統需求
- [x] PostgreSQL 資料庫
- [x] Apache Airflow 環境
- [x] Python 3.8+ 環境
- [x] 網路連線（用於API存取）

### 檔案清單
- [x] `job_config.json` - 作業配置檔案
- [x] `cultural_heritage_statistics.py` - 主要ETL腳本
- [x] `create_table.sql` - 資料庫表格建立腳本
- [x] `setup_component.sql` - 組件配置插入腳本
- [x] `cleanup_and_setup.sql` - 清理並重新設定腳本
- [x] `test_component.py` - 測試腳本
- [x] `README.md` - 組件說明文檔
- [x] `__init__.py` - Python模組初始化檔案

## 🚀 部署步驟

### 步驟 1: 資料庫初始化

```bash
# 1.1 建立數據表結構
psql -h <database_host> -U <username> -d <database_name> -f create_table.sql

# 1.2 插入組件配置（如果是首次安裝）
psql -h <database_host> -U <username> -d <database_name> -f setup_component.sql

# 1.3 如果之前安裝失敗，使用清理腳本重新安裝
psql -h <database_host> -U <username> -d <database_name> -f cleanup_and_setup.sql
```

### 步驟 2: 驗證資料庫配置

```sql
-- 檢查表格是否建立成功
SELECT table_name FROM information_schema.tables 
WHERE table_name IN ('cultural_heritage_statistics', 'cultural_heritage_statistics_history');

-- 檢查組件配置是否插入成功
SELECT c.index, c.name FROM components c WHERE c.index = 'cultural_heritage_statistics';
SELECT qc.index, qc.city, qc.query_type FROM query_charts qc WHERE qc.index = 'cultural_heritage_statistics';
SELECT cc.index FROM component_charts cc WHERE cc.index = 'cultural_heritage_statistics';
```

### 步驟 3: 部署Airflow DAG

```bash
# 3.1 複製組件資料夾到Airflow DAGs目錄
cp -r cultural_heritage_statistics/ /opt/airflow/dags/proj_city_dashboard/

# 3.2 設定檔案權限
chmod -R 755 /opt/airflow/dags/proj_city_dashboard/cultural_heritage_statistics/

# 3.3 重啟Airflow服務
docker-compose restart airflow-webserver airflow-scheduler
# 或
systemctl restart airflow-webserver airflow-scheduler
```

### 步驟 4: 驗證DAG部署

1. 開啟Airflow Web UI (`http://localhost:8080`)
2. 檢查DAG列表中是否出現 `cultural_heritage_statistics`
3. 確認DAG狀態為啟用（綠色）
4. 檢查DAG配置是否正確

### 步驟 5: 執行測試

```bash
# 5.1 執行組件測試腳本
cd /opt/airflow/dags/proj_city_dashboard/cultural_heritage_statistics/
python test_component.py

# 5.2 手動觸發DAG執行
# 在Airflow Web UI中點擊 "Trigger DAG" 按鈕
# 或使用命令列
airflow dags trigger cultural_heritage_statistics
```

### 步驟 6: 驗證數據處理

```sql
-- 檢查數據是否成功載入
SELECT city, district, category, count(*) as records 
FROM cultural_heritage_statistics 
GROUP BY city, district, category 
ORDER BY city, district, category;

-- 檢查最新數據時間
SELECT MAX(update_time) as latest_update FROM cultural_heritage_statistics;
```

## 🔧 配置說明

### 環境變數
確保以下環境變數已正確設定：

```bash
# Airflow配置
AIRFLOW__CORE__DAGS_FOLDER=/opt/airflow/dags
AIRFLOW__CORE__EXECUTOR=LocalExecutor

# 資料庫連線
AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql://user:password@host:port/database
```

### 連線配置
在Airflow Web UI中設定以下連線：

1. **postgres_default**
   - Connection Type: Postgres
   - Host: `<database_host>`
   - Schema: `<database_name>`
   - Login: `<username>`
   - Password: `<password>`
   - Port: `5432`

## 📊 監控與維護

### 監控指標
- DAG執行成功率
- 數據更新時效性
- API回應時間
- 資料庫查詢效能

### 日誌檢查
```bash
# 檢查Airflow任務日誌
tail -f /opt/airflow/logs/cultural_heritage_statistics/*/task_id/*/attempt=1.log

# 檢查PostgreSQL日誌
tail -f /var/log/postgresql/postgresql-*.log
```

### 定期維護
- 每月檢查API端點可用性
- 每季檢查地址解析準確度
- 每年檢查行政區清單更新

## 🚨 故障排除

### 常見問題

#### 1. DAG未出現在Airflow UI
**原因**: 檔案權限或語法錯誤
**解決方案**:
```bash
# 檢查檔案權限
ls -la /opt/airflow/dags/proj_city_dashboard/cultural_heritage_statistics/

# 檢查Python語法
python -m py_compile cultural_heritage_statistics.py

# 檢查Airflow日誌
airflow dags list | grep cultural_heritage_statistics
```

#### 2. 資料庫連線失敗
**原因**: 連線配置錯誤或網路問題
**解決方案**:
```bash
# 測試資料庫連線
psql -h <host> -U <user> -d <database> -c "SELECT 1;"

# 檢查Airflow連線配置
airflow connections get postgres_default
```

#### 3. API存取失敗
**原因**: 網路問題或API端點變更
**解決方案**:
```bash
# 測試API連線
curl -I https://iheritage.gov.taipei/data/api/designation/data
curl -I https://data.ntpc.gov.tw/api/datasets/d8eb898f-6c59-4689-9191-48dbbef16606/csv

# 檢查防火牆設定
telnet iheritage.gov.taipei 443
```

#### 4. 數據處理錯誤
**原因**: 數據格式變更或地址解析失敗
**解決方案**:
```bash
# 執行測試腳本診斷
python test_component.py

# 檢查數據樣本
python -c "
import requests
response = requests.get('https://iheritage.gov.taipei/data/api/designation/data')
print(response.json()[:2])
"
```

#### 5. 組件配置插入失敗 - NOT NULL 約束錯誤 🆕
**錯誤訊息**: `null value in column "created_at" of relation "query_charts" violates not-null constraint`

**原因**: `query_charts` 表中的 `created_at` 和 `updated_at` 欄位是必填的

**解決方案**:
```bash
# 選項1: 使用修正後的setup_component.sql
psql -h <host> -U <user> -d <database> -f setup_component.sql

# 選項2: 如果已有部分數據，使用清理腳本重新安裝
psql -h <host> -U <user> -d <database> -f cleanup_and_setup.sql

# 選項3: 手動清理後重新安裝
psql -h <host> -U <user> -d <database> -c "
DELETE FROM component_charts WHERE index = 'cultural_heritage_statistics';
DELETE FROM query_charts WHERE index = 'cultural_heritage_statistics';
DELETE FROM components WHERE index = 'cultural_heritage_statistics';
"
psql -h <host> -U <user> -d <database> -f setup_component.sql
```

**驗證修復**:
```sql
-- 檢查插入是否成功，並確認時間戳欄位有值
SELECT index, city, created_at, updated_at 
FROM query_charts 
WHERE index = 'cultural_heritage_statistics';
```

## 📈 效能優化

### 資料庫優化
```sql
-- 建立額外索引（如需要）
CREATE INDEX CONCURRENTLY idx_cultural_heritage_update_time 
ON cultural_heritage_statistics(update_time DESC);

-- 定期清理歷史數據（保留2年）
DELETE FROM cultural_heritage_statistics_history 
WHERE update_time < NOW() - INTERVAL '2 years';
```

### Airflow優化
```python
# 在job_config.json中調整並行度
"max_active_runs": 1,
"max_active_tasks": 2,
"catchup": false
```

## 📞 支援聯絡

如遇到部署問題，請聯絡：
- 技術支援: [技術團隊聯絡方式]
- 文檔更新: [文檔維護團隊]
- 緊急問題: [緊急聯絡方式]

---

**部署完成檢查清單**:
- [ ] 資料庫表格建立成功
- [ ] 組件配置插入成功（包含 created_at, updated_at 欄位）
- [ ] DAG在Airflow UI中顯示
- [ ] 測試腳本執行通過
- [ ] 手動觸發DAG成功
- [ ] 數據成功載入資料庫
- [ ] API端點回應正常
- [ ] 監控指標設定完成 