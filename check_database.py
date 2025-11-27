#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查数据库中的基础采购链接数据
"""

import sqlite3

def check_database():
    try:
        # 连接到正确的数据库文件
        conn = sqlite3.connect("data/hospital_scanner_new.db")
        cursor = conn.cursor()

        print("检查基础采购链接字段是否存在...")

        # 检查表结构
        cursor.execute("PRAGMA table_info(hospitals)")
        columns = cursor.fetchall()

        has_base_procurement_link = False
        for col in columns:
            if col[1] == "base_procurement_link":
                has_base_procurement_link = True
                break

        if has_base_procurement_link:
            print("✅ base_procurement_link 字段存在于 hospitals 表中")
        else:
            print("❌ base_procurement_link 字段不存在于 hospitals 表中")

        # 查找北京和睦家医院
        cursor.execute("""
            SELECT id, name, base_procurement_link
            FROM hospitals
            WHERE name LIKE '%和睦家%' OR name = '北京和睦家医院'
            LIMIT 5
        """)

        results = cursor.fetchall()

        if results:
            print(f"\n找到 {len(results)} 个相关医院:")
            for row in results:
                print(f"  ID: {row[0]}, 名称: {row[1]}, 基础采购链接: {row[2]}")
        else:
            print("\n❌ 未找到北京和睦家医院")

        # 查询一些最近更新的记录
        cursor.execute("""
            SELECT id, name, base_procurement_link, updated_at
            FROM hospitals
            WHERE base_procurement_link IS NOT NULL
            ORDER BY updated_at DESC
            LIMIT 5
        """)

        recent_results = cursor.fetchall()

        if recent_results:
            print(f"\n最近更新的基础采购链接 ({len(recent_results)} 条):")
            for row in recent_results:
                print(f"  ID: {row[0]}, 名称: {row[1]}, 链接: {row[2]}, 更新时间: {row[3]}")
        else:
            print("\n⚠️ 没有找到设置了基础采购链接的医院")

        # 统计总数
        cursor.execute("SELECT COUNT(*) FROM hospitals")
        total_hospitals = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM hospitals WHERE base_procurement_link IS NOT NULL")
        with_link = cursor.fetchone()[0]

        print(f"\n📊 统计信息:")
        print(f"  总医院数: {total_hospitals}")
        print(f"  有基础采购链接的医院: {with_link}")
        print(f"  设置率: {(with_link/total_hospitals*100):.2f}%" if total_hospitals > 0 else "  设置率: 0%")

    except Exception as e:
        print(f"❌ 数据库检查失败: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_database()