import mysql.connector

try:
    # 1. Tạo kết nối đến MySQL
    db = mysql.connector.connect(
        host="localhost",
        user="root",          # Thay bằng username MySQL của bạn (mặc định XAMPP/MySQL là root)
        password="2609",          # Thay bằng mật khẩu MySQL của bạn (nếu có)
        database="dbms_vanminh"
    )
    
    print("✅ Kết nối Database thành công!")

    # 2. Tạo một "con trỏ" để chạy lệnh SQL (dictionary=True giúp data trả về dạng dict rất dễ dùng)
    cursor = db.cursor(dictionary=True)

    # 3. Viết lệnh lấy dữ liệu (Ví dụ: Lấy danh sách bến xe)
    cursor.execute("SELECT * FROM Location")
    locations = cursor.fetchall()

    # 4. In thử dữ liệu ra màn hình
    print("\n--- DANH SÁCH BẾN XE ---")
    for loc in locations:
        print(f"Bến: {loc['station']} - Tỉnh: {loc['province']}")

except mysql.connector.Error as err:
    print(f"❌ Lỗi kết nối: {err}")
finally:
    # Luôn nhớ đóng kết nối khi xong việc
    if 'db' in locals() and db.is_connected():
        cursor.close()
        db.close()