from mysql.connector import pooling

# Pool được khởi tạo 1 lần duy nhất, dùng chung với app.py
_db_pool = None

def init_pool(pool: pooling.MySQLConnectionPool):
    """Nhận pool từ app.py để dùng chung, không tạo pool riêng."""
    global _db_pool
    _db_pool = pool

def verify_account(username_input, password_input):
    """
    Kiểm tra thông tin đăng nhập từ Database.
    - Trả về: (True, thông_tin_khách_hàng) nếu đúng.
    - Trả về: (False, None) nếu sai tài khoản/mật khẩu hoặc lỗi DB.
    Dùng connection pool (không tạo kết nối mới).
    """
    db = None
    cursor = None
    try:
        # Lấy kết nối từ pool (không tạo mới)
        db = _db_pool.get_connection()
        cursor = db.cursor(dictionary=True)

        # Tìm user theo username
        query = "SELECT * FROM Customer WHERE username = %s"
        cursor.execute(query, (username_input,))
        user = cursor.fetchone()

        # Kiểm tra logic mật khẩu
        if user:
            if user['password'] == password_input:
                return True, user
            else:
                print("Sai mật khẩu")
                return False, None
        else:
            print("Tên đăng nhập không tồn tại")
            return False, None

    except Exception as err:
        print(f"Lỗi hệ thống: {err}")
        return False, None

    finally:
        # Trả kết nối về pool (không đóng hẳn)
        if cursor:
            cursor.close()
        if db and db.is_connected():
            db.close()