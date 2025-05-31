from airflow import DAG
from operators.common_pipeline import CommonDag


def _cultural_heritage_statistics(**kwargs):
    import pandas as pd
    import requests
    import json
    import re
    from datetime import datetime
    from sqlalchemy import create_engine
    from utils.load_stage import (
        save_dataframe_to_postgresql,
        update_lasttime_in_data_to_dataset_info,
    )
    from utils.transform_time import get_tpe_now_time_str

    # Config
    ready_data_db_uri = kwargs.get("ready_data_db_uri")
    dag_infos = kwargs.get("dag_infos")
    dag_id = dag_infos.get("dag_id")
    load_behavior = dag_infos.get("load_behavior")
    default_table = dag_infos.get("ready_data_default_table")
    history_table = dag_infos.get("ready_data_history_table")
    
    # Data source URLs
    TAIPEI_URL = "https://iheritage.gov.taipei/data/api/designation/data"
    NTPC_URL = "https://data.ntpc.gov.tw/api/datasets/d8eb898f-6c59-4689-9191-48dbbef16606/csv"

    def extract_district_from_address(address):
        """Extract district from address string"""
        if not address or pd.isna(address):
            return "未知"
        
        # For New Taipei City format: "新北市xxx區..."
        ntpc_match = re.search(r'新北市(\w+區)', address)
        if ntpc_match:
            return ntpc_match.group(1)
        
        # For Taipei City format: various patterns
        # Pattern 1: "臺北市xxx區" or "台北市xxx區"
        taipei_match = re.search(r'[台臺]北市(\w+區)', address)
        if taipei_match:
            return taipei_match.group(1)
        
        # Pattern 2: Direct district name at the beginning (only for valid districts)
        district_match = re.search(r'^(\w+區)', address)
        if district_match:
            district = district_match.group(1)
            # Check if it's a valid Taipei/New Taipei district
            valid_districts = [
                '中正區', '大同區', '中山區', '松山區', '大安區', '萬華區', '信義區', '士林區', '北投區', '內湖區', '南港區', '文山區',  # 台北市
                '板橋區', '三重區', '中和區', '永和區', '新莊區', '新店區', '樹林區', '鶯歌區', '三峽區', '淡水區', '汐止區', '瑞芳區', '土城區', '蘆洲區', '五股區', '泰山區', '林口區', '深坑區', '石碇區', '坪林區', '三芝區', '石門區', '八里區', '平溪區', '雙溪區', '貢寮區', '金山區', '萬里區', '烏來區'  # 新北市
            ]
            if district in valid_districts:
                return district
        
        return "未知"

    def process_taipei_data():
        """Process Taipei cultural heritage data"""
        try:
            response = requests.get(TAIPEI_URL, timeout=30)
            response.raise_for_status()
            taipei_data = response.json()
            
            processed_data = []
            for item in taipei_data:
                # Extract district from address
                addresses = item.get('現況地址', [])
                district = "未知"
                if addresses and len(addresses) > 0:
                    district = extract_district_from_address(addresses[0])
                
                # Get heritage category
                category = item.get('資產類別', '未分類')
                
                processed_data.append({
                    'city': '台北市',
                    'district': district,
                    'category': category,
                    'count': 1
                })
            
            return pd.DataFrame(processed_data)
        except Exception as e:
            print(f"Error processing Taipei data: {e}")
            return pd.DataFrame()

    def process_ntpc_data():
        """Process New Taipei City cultural heritage data"""
        try:
            response = requests.get(NTPC_URL, timeout=30)
            response.raise_for_status()
            
            # Parse CSV data
            from io import StringIO
            csv_data = StringIO(response.text)
            ntpc_df = pd.read_csv(csv_data)
            
            processed_data = []
            for _, row in ntpc_df.iterrows():
                # Extract district from address
                address = row.get('address', '')
                district = extract_district_from_address(address)
                
                # Get heritage category (use 'affection' field)
                category = row.get('affection', '未分類')
                
                processed_data.append({
                    'city': '新北市',
                    'district': district,
                    'category': category,
                    'count': 1
                })
            
            return pd.DataFrame(processed_data)
        except Exception as e:
            print(f"Error processing New Taipei data: {e}")
            return pd.DataFrame()

    # Extract data from both sources
    taipei_df = process_taipei_data()
    ntpc_df = process_ntpc_data()
    
    # Combine data
    if not taipei_df.empty and not ntpc_df.empty:
        combined_df = pd.concat([taipei_df, ntpc_df], ignore_index=True)
    elif not taipei_df.empty:
        combined_df = taipei_df
    elif not ntpc_df.empty:
        combined_df = ntpc_df
    else:
        print("No data available from both sources")
        return

    # Group by city, district, and category to get counts
    aggregated_df = combined_df.groupby(['city', 'district', 'category']).agg({
        'count': 'sum'
    }).reset_index()
    
    # Add metadata
    current_time = get_tpe_now_time_str(to_str=True)
    aggregated_df['data_time'] = current_time
    aggregated_df['update_time'] = current_time
    
    # Reorder columns
    ready_data = aggregated_df[[
        'city',
        'district', 
        'category',
        'count',
        'data_time',
        'update_time'
    ]]

    # Load data to database
    engine = create_engine(ready_data_db_uri)
    save_dataframe_to_postgresql(
        engine,
        data=ready_data,
        load_behavior=load_behavior,
        default_table=default_table,
        history_table=history_table,
    )
    
    # Update lasttime_in_data
    lasttime_in_data = ready_data["update_time"].max()
    update_lasttime_in_data_to_dataset_info(
        engine, airflow_dag_id=dag_id, lasttime_in_data=lasttime_in_data
    )


dag = CommonDag(proj_folder="proj_city_dashboard", dag_folder="cultural_heritage_statistics")
dag.create_dag(etl_func=_cultural_heritage_statistics) 