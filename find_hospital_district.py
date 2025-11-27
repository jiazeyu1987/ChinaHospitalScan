import sqlite3

def find_district():
    try:
        conn = sqlite3.connect("data/hospital_scanner_new.db")
        cursor = conn.cursor()

        # 查找北京和睦家医院的district_id
        cursor.execute("SELECT id, name, district_id FROM hospitals WHERE name LIKE '%和睦家%' AND name = '北京和睦家医院'")
        result = cursor.fetchone()

        if result:
            print(f"Found hospital: ID={result[0]}, Name={result[1]}, District_ID={result[2]}")

            # 查询该区县的所有医院
            cursor.execute("SELECT id, name, base_procurement_link FROM hospitals WHERE district_id = ? LIMIT 3", (result[2],))
            hospitals = cursor.fetchall()

            print(f"\nHospitals in same district (ID={result[2]}):")
            for hospital in hospitals:
                print(f"  ID: {hospital[0]}, Name: {hospital[1]}, Base Link: {hospital[2]}")
        else:
            print("Beijing Hejia Hospital not found")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    find_district()