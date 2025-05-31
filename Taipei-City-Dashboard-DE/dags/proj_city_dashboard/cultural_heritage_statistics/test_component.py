#!/usr/bin/env python3
"""
文化資產統計組件測試腳本
用於測試數據處理邏輯和API連接
"""

import pandas as pd
import requests
import json
import re
from datetime import datetime


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


def test_taipei_api():
    """測試台北市API連接和數據格式"""
    print("🧪 測試台北市API...")
    
    try:
        url = "https://iheritage.gov.taipei/data/api/designation/data"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ 成功獲取 {len(data)} 筆台北市文化資產數據")
        
        # 測試前5筆數據的地址解析
        print("\n📍 測試地址解析（前5筆）：")
        for i, item in enumerate(data[:5]):
            addresses = item.get('現況地址', [])
            address = addresses[0] if addresses else ""
            district = extract_district_from_address(address)
            category = item.get('資產類別', '未分類')
            
            print(f"  {i+1}. {item.get('個案名稱', 'N/A')}")
            print(f"     地址: {address}")
            print(f"     行政區: {district}")
            print(f"     類別: {category}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ 台北市API測試失敗: {e}")
        return False


def test_ntpc_api():
    """測試新北市API連接和數據格式"""
    print("🧪 測試新北市API...")
    
    try:
        url = "https://data.ntpc.gov.tw/api/datasets/d8eb898f-6c59-4689-9191-48dbbef16606/csv"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Parse CSV data
        from io import StringIO
        csv_data = StringIO(response.text)
        df = pd.read_csv(csv_data)
        
        print(f"✅ 成功獲取 {len(df)} 筆新北市文化資產數據")
        
        # 測試前5筆數據的地址解析
        print("\n📍 測試地址解析（前5筆）：")
        for i, row in df.head().iterrows():
            address = row.get('address', '')
            district = extract_district_from_address(address)
            category = row.get('affection', '未分類')
            
            print(f"  {i+1}. {row.get('name', 'N/A')}")
            print(f"     地址: {address}")
            print(f"     行政區: {district}")
            print(f"     類別: {category}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ 新北市API測試失敗: {e}")
        return False


def test_data_processing():
    """測試完整的數據處理流程"""
    print("🧪 測試數據處理流程...")
    
    # 模擬測試數據
    test_data = [
        {'city': '台北市', 'district': '中正區', 'category': '古蹟'},
        {'city': '台北市', 'district': '中正區', 'category': '古蹟'},
        {'city': '台北市', 'district': '中正區', 'category': '歷史建築'},
        {'city': '台北市', 'district': '大安區', 'category': '古蹟'},
        {'city': '新北市', 'district': '淡水區', 'category': '古蹟'},
        {'city': '新北市', 'district': '淡水區', 'category': '古蹟'},
        {'city': '新北市', 'district': '板橋區', 'category': '歷史建築'},
    ]
    
    # 創建DataFrame並處理
    df = pd.DataFrame(test_data)
    df['count'] = 1
    
    # 按城市、行政區、類別彙總
    result = df.groupby(['city', 'district', 'category']).agg({'count': 'sum'}).reset_index()
    
    print("✅ 數據彙總結果：")
    print(result.to_string(index=False))
    
    # 驗證結果
    expected_rows = [
        ('台北市', '中正區', '古蹟', 2),
        ('台北市', '中正區', '歷史建築', 1),
        ('台北市', '大安區', '古蹟', 1),
        ('新北市', '淡水區', '古蹟', 2),
        ('新北市', '板橋區', '歷史建築', 1),
    ]
    
    success = True
    for expected in expected_rows:
        city, district, category, count = expected
        matching_rows = result[
            (result['city'] == city) & 
            (result['district'] == district) & 
            (result['category'] == category)
        ]
        
        if len(matching_rows) == 1 and matching_rows.iloc[0]['count'] == count:
            print(f"✅ {city} {district} {category}: {count} 筆")
        else:
            print(f"❌ {city} {district} {category}: 預期 {count} 筆，實際 {matching_rows.iloc[0]['count'] if len(matching_rows) else 0} 筆")
            success = False
    
    return success


def test_address_patterns():
    """測試各種地址格式的解析"""
    print("🧪 測試地址解析模式...")
    
    test_addresses = [
        ("台北市中正區中山南路7號", "中正區"),
        ("臺北市大安區永康街31巷11號", "大安區"),
        ("大安區永康街31巷11-1號", "大安區"),
        ("新北市淡水區中正路28巷1號", "淡水區"),
        ("新北市新莊區新莊路150號", "新莊區"),
        ("淡水區中正路95巷22號", "淡水區"),
        ("板橋區西門街5號", "板橋區"),
        ("", "未知"),
        ("台中市西區某路123號", "未知"),  # 不在台北/新北的地址
    ]
    
    success = True
    for address, expected in test_addresses:
        result = extract_district_from_address(address)
        if result == expected:
            print(f"✅ '{address}' -> '{result}'")
        else:
            print(f"❌ '{address}' -> '{result}' (預期: '{expected}')")
            success = False
    
    return success


def main():
    """主測試函數"""
    print("🚀 開始文化資產統計組件測試")
    print("=" * 50)
    
    tests = [
        ("地址解析模式", test_address_patterns),
        ("數據處理流程", test_data_processing),
        ("台北市API連接", test_taipei_api),
        ("新北市API連接", test_ntpc_api),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}")
        print("-" * 30)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ 測試異常: {e}")
            results.append((test_name, False))
    
    # 總結報告
    print("\n" + "=" * 50)
    print("📊 測試結果總結")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n總計: {passed}/{len(results)} 項測試通過")
    
    if passed == len(results):
        print("🎉 所有測試通過！組件可以部署。")
        return 0
    else:
        print("⚠️  部分測試失敗，請檢查相關問題。")
        return 1


if __name__ == "__main__":
    exit(main()) 