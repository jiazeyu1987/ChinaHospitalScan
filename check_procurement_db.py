#!/usr/bin/env python3
import sqlite3
import json

def check_procurement_links():
    db_path = "data/hospital_scanner_new.db"

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print("检查 procurement_links 表...")

        # 检查表结构
        cursor.execute("PRAGMA table_info(procurement_links)")
        columns = cursor.fetchall()
        print(f"表结构: {[col[1] for col in columns]}")

        # 检查记录数
        cursor.execute("SELECT COUNT(*) FROM procurement_links")
        total_count = cursor.fetchone()[0]
        print(f"总记录数: {total_count}")

        if total_count > 0:
            # 查看最近的记录
            cursor.execute("""
                SELECT base_url, url, link_text, first_seen_at, last_seen_at, is_latest
                FROM procurement_links
                ORDER BY last_seen_at DESC
                LIMIT 5
            """)
            records = cursor.fetchall()

            print("\n最近的5条记录:")
            for i, record in enumerate(records, 1):
                base_url, url, link_text, first_seen, last_seen, is_latest = record
                print(f"\n{i}. 基础URL: {base_url}")
                print(f"   URL: {url[:80]}...")
                print(f"   链接文本: '{link_text}'")
                print(f"   首次发现: {first_seen}")
                print(f"   最后更新: {last_seen}")
                print(f"   是否最新: {is_latest}")

        # 检查不同base_url的统计
        cursor.execute("""
            SELECT base_url, COUNT(*) as count
            FROM procurement_links
            GROUP BY base_url
            ORDER BY count DESC
        """)
        stats = cursor.fetchall()

        if stats:
            print(f"\n按基础URL统计:")
            for base_url, count in stats:
                print(f"  {base_url}: {count} 条记录")

    except Exception as e:
        print(f"检查数据库失败: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_procurement_links()