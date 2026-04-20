import mysql.connector

def verify_account(username_input, password_input):
    """
    Hàm kết nối DB và kiểm tra thông tin đăng nhập.
    - Trả về: (True, thông_tin_khách_hàng) nếu đúng.
    - Trả về: (False, None) nếu sai tài khoản/mật khẩu hoặc lỗi DB.
    """
    db = None
    cursor = None
    try:
        # Kết nối tới database
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="2609",
            database="dbms_vanminh"
        )
        
        # Dùng dictionary=True để dữ liệu trả về dạng dict (vd: user['name'])
        cursor = db.cursor(dictionary=True)

        # tìm user
        query = "SELECT * FROM Customer WHERE username = %s"
        cursor.execute(query, (username_input,))
        
        user = cursor.fetchone()

        # Kiểm tra logic mật khẩu
        if user:
            # So sánh mật khẩu
            if user['password'] == password_input:
                return True, user
            else:
                print("Sai mật khẩu")
                return False, None
        else:
            print("Tên đăng nhập không tồn tại")
            return False, None

    except mysql.connector.Error as err:
        print(f"Lỗi hệ thống")
        return False, None
        
    finally:
        # giải phóng tài nguyên
        if cursor:
            cursor.close()
        if db and db.is_connected():
            db.close()