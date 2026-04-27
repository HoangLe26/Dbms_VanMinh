import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="2609",
    database="dbms_vanminh"
)
cursor = db.cursor()
# Lấy toàn bộ seat để update
cursor.execute("SELECT seat_id, seat_code FROM Seat")
seats = cursor.fetchall()
for seat_id, seat_code in seats:
    # Xóa ký tự \r \n nếu có
    clean_code = seat_code.replace('\r', '').replace('\n', '').strip()
    cursor.execute("UPDATE Seat SET seat_code = %s WHERE seat_id = %s", (clean_code, seat_id))

db.commit()
print("Da lam sach bang Seat!")
cursor.close()
db.close()
