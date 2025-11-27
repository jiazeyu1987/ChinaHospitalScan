import sqlite3

def check_db():
    try:
        conn = sqlite3.connect("data/hospital_scanner_new.db")
        cursor = conn.cursor()

        # 检查表结构
        cursor.execute("PRAGMA table_info(hospitals)")
        columns = cursor.fetchall()

        print("Hospitals table columns:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")

        # 查找北京和睦家医院
        cursor.execute("SELECT id, name, base_procurement_link FROM hospitals WHERE name LIKE '%和睦家%'")
        results = cursor.fetchall()

        print(f"\nFound {len(results)} hospitals matching '和睦家':")
        for row in results:
            print(f"  ID: {row[0]}, Name: {row[1]}, Link: {row[2]}")

        # 统计
        cursor.execute("SELECT COUNT(*) FROM hospitals")
        total = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM hospitals WHERE base_procurement_link IS NOT NULL")
        with_link = cursor.fetchone()[0]

        print(f"\nStats:")
        print(f"  Total hospitals: {total}")
        print(f"  With procurement links: {with_link}")

        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_db()