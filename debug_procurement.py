#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import json
from datetime import datetime, timedelta

def debug_hospital_procurement(hospital_name):
    """调试医院的采购信息"""

    # 连接数据库
    db_path = 'data/hospital_scanner_new.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print(f"=== 调试医院: {hospital_name} ===")

    # 1. 查找医院信息
    cursor.execute('''
        SELECT id, name, base_procurement_link
        FROM hospitals
        WHERE name = ?
    ''', (hospital_name,))

    hospitals = cursor.fetchall()
    print(f"\n找到医院: {len(hospitals)} 个")

    for hospital in hospitals:
        hospital_id, hospital_name, base_url = hospital
        print(f"\n医院 ID: {hospital_id}")
        print(f"医院名称: {hospital_name}")
        print(f"基础采购链接: {base_url}")

        if not base_url:
            print("❌ 未设置基础采购链接")
            continue

        # 2. 查找采购数据
        cursor.execute('''
            SELECT COUNT(*) as count
            FROM procurement_links
            WHERE base_url = ?
            AND is_latest = 1
        ''', (base_url,))

        total_count = cursor.fetchone()[0]
        print(f"采购数据总数: {total_count} 条")

        if total_count == 0:
            print("❌ 没有采购数据")
            continue

        # 3. 检查一周内的数据
        today = datetime.now()
        one_week_ago = today - timedelta(days=7)

        cursor.execute('''
            SELECT COUNT(*) as count
            FROM procurement_links
            WHERE base_url = ?
            AND is_latest = 1
            AND DATE(first_seen_at) >= DATE(?)
            AND DATE(first_seen_at) <= DATE(?)
        ''', (base_url, one_week_ago.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')))

        week_count = cursor.fetchone()[0]
        print(f"一周内数据: {week_count} 条")

        # 4. 显示最近几条记录
        cursor.execute('''
            SELECT link_text, url, first_seen_at
            FROM procurement_links
            WHERE base_url = ?
            AND is_latest = 1
            ORDER BY first_seen_at DESC
            LIMIT 5
        ''', (base_url,))

        recent_records = cursor.fetchall()
        print("\n最近5条记录:")
        for i, (title, url, date) in enumerate(recent_records, 1):
            print(f"  {i}. {title}")
            print(f"     日期: {date}")
            print(f"     URL: {url}")
            print()

    conn.close()

def list_all_hospitals_with_data():
    """列出所有有采购数据的医院"""

    db_path = 'data/hospital_scanner_new.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("=== 所有有采购数据的医院 ===")

    cursor.execute('''
        SELECT DISTINCT base_url, COUNT(*) as count
        FROM procurement_links
        WHERE is_latest = 1
        GROUP BY base_url
        ORDER BY count DESC
    ''')

    base_urls = cursor.fetchall()

    for base_url, count in base_urls:
        print(f"\nBase URL: {base_url}")
        print(f"数据量: {count} 条")

        # 查找对应医院
        cursor.execute('''
            SELECT id, name FROM hospitals
            WHERE base_procurement_link = ?
        ''', (base_url,))

        hospital = cursor.fetchone()
        if hospital:
            print(f"对应医院: ID={hospital[0]}, 名称={hospital[1]}")
        else:
            print("未找到对应医院")

    conn.close()

if __name__ == '__main__':
    # 列出所有有数据的医院
    list_all_hospitals_with_data()

    print("\n" + "="*50)

    # 调试特定医院（请替换为您查看的医院名称）
    # hospital_name = input("请输入您查看的医院名称: ")
    hospital_name = "重庆医科大学附属儿童医院"  # 默认测试
    debug_hospital_procurement(hospital_name)