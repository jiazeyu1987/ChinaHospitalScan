import sqlite3
import os

def check_procurement_links():
    try:
        db_path = os.path.join("data", "hospital_scanner_new.db")
        print(f"检查数据库文件: {db_path}")
        print(f"文件是否存在: {os.path.exists(db_path)}")

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 查看所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"数据库中的表: {[table[0] for table in tables]}")

        # 检查procurement_links表结构
        try:
            cursor.execute("PRAGMA table_info(procurement_links)")
            columns = cursor.fetchall()
            print(f"procurement_links表结构: {columns}")
        except Exception as e:
            print(f"procurement_links表结构查询失败: {e}")

        # 查看procurement_links表记录数
        try:
            cursor.execute("SELECT COUNT(*) FROM procurement_links")
            count = cursor.fetchone()[0]
            print(f"procurement_links表总记录数: {count}")

            if count > 0:
                cursor.execute("SELECT * FROM procurement_links LIMIT 5")
                records = cursor.fetchall()
                print(f"最近5条记录: {records}")

                # 查看是否有特定的base_url记录
                cursor.execute("SELECT base_url, COUNT(*) FROM procurement_links GROUP BY base_url")
                base_urls = cursor.fetchall()
                print(f"按base_url分组: {base_urls}")
            else:
                print("procurement_links表为空")

        except Exception as e:
            print(f"查询procurement_links表失败: {e}")

        conn.close()

    except Exception as e:
        print(f"数据库操作失败: {e}")

if __name__ == "__main__":
    check_procurement_links()