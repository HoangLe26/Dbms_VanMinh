import mysql.connector

def fix_seats():
    db = mysql.connector.connect(
        host="localhost",
        user="root", 
        password="2609", 
        database="dbms_vanminh"
    )
    cursor = db.cursor()
    cursor.execute("UPDATE Seat SET seat_code = REPLACE(seat_code, '\\r', '')")
    db.commit()
    print(f"Updated {cursor.rowcount} rows")
    cursor.close()
    db.close()

if __name__ == "__main__":
    fix_seats()
