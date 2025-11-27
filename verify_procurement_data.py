import sqlite3
import os
import sys

def verify_procurement_data():
    """详细验证procurement_links表的数据"""

    # 数据库文件路径
    db_path = "D:\\ProjectPackage\\HBScan\\app\\data\\hospital_scanner_new.db"
    print(f"🔍 检查数据库文件: {db_path}")
    print(f"📁 文件是否存在: {os.path.exists(db_path)}")

    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        return

    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print("\n📋 数据库中的所有表:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        for table in tables:
            print(f"  - {table}")

        # 检查procurement_links表是否存在
        if "procurement_links" not in tables:
            print(f"\n❌ procurement_links表不存在！")
            return

        print(f"\n🏗️ procurement_links表结构:")
        cursor.execute("PRAGMA table_info(procurement_links)")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[1]} ({col[2]}) {'NOT NULL' if col[3] else ''} {'PRIMARY KEY' if col[5] else ''}")

        # 检查记录总数
        cursor.execute("SELECT COUNT(*) FROM procurement_links")
        total_count = cursor.fetchone()[0]
        print(f"\n📊 procurement_links表总记录数: {total_count}")

        if total_count == 0:
            print("❌ 表为空，没有数据！")
            return

        # 显示最近的一些记录
        print(f"\n📄 最近5条记录:")
        cursor.execute("""
            SELECT id, base_url, url, link_text, first_seen_at, last_seen_at, is_latest
            FROM procurement_links
            ORDER BY id DESC
            LIMIT 5
        """)
        records = cursor.fetchall()
        for i, record in enumerate(records, 1):
            print(f"  {i}. ID: {record[0]}")
            print(f"     Base URL: {record[1][:80]}{'...' if len(record[1]) > 80 else ''}")
            print(f"     URL: {record[2][:80]}{'...' if len(record[2]) > 80 else ''}")
            print(f"     Link Text: {record[3][:50] if record[3] else 'NULL'}{'...' if record[3] and len(record[3]) > 50 else ''}")
            print(f"     First Seen: {record[4]}")
            print(f"     Last Seen: {record[5]}")
            print(f"     Is Latest: {record[6]}")
            print()

        # 按base_url分组统计
        print(f"📈 按base_url分组统计:")
        cursor.execute("""
            SELECT base_url, COUNT(*) as count
            FROM procurement_links
            GROUP BY base_url
            ORDER BY count DESC
        """)
        base_urls = cursor.fetchall()
        for base_url, count in base_urls:
            print(f"  {base_url}: {count} 条记录")

        # 检查最新记录
        cursor.execute("SELECT base_url, COUNT(*) FROM procurement_links WHERE is_latest = 1 GROUP BY base_url")
        latest_records = cursor.fetchall()
        print(f"\n🌟 最新记录 (is_latest=1):")
        for base_url, count in latest_records:
            print(f"  {base_url}: {count} 条记录")

        conn.close()

    except Exception as e:
        print(f"❌ 数据库操作失败: {e}")
        import traceback
        traceback.print_exc()

def check_alternative_db_files():
    """检查可能的备份数据库文件"""
    print(f"\n🔍 检查其他可能的数据库文件...")

    possible_paths = [
        "data/hospital_scanner_new.db",
        "data/hospital_scanner.db",
        "../data/hospital_scanner_new.db",
        "./data/hospital_scanner_new.db",
        "D:/ProjectPackage/HBScan/app/data/hospital_scanner_new.db"
    ]

    for path in possible_paths:
        if os.path.exists(path):
            abs_path = os.path.abspath(path)
            print(f"📁 发现数据库文件: {abs_path}")

            try:
                conn = sqlite3.connect(abs_path)
                cursor = conn.cursor()

                # 检查表
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]

                if "procurement_links" in tables:
                    cursor.execute("SELECT COUNT(*) FROM procurement_links")
                    count = cursor.fetchone()[0]
                    print(f"  - procurement_links记录数: {count}")
                else:
                    print(f"  - 没有procurement_links表")

                conn.close()

            except Exception as e:
                print(f"  - 无法读取: {e}")

if __name__ == "__main__":
    print("🚀 开始验证procurement_links数据...")
    verify_procurement_data()
    check_alternative_db_files()