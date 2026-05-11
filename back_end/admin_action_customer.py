from back_end.admin_queries import get_db_connection

def edit_customer_action(data):
    """Cập nhật thông tin khách hàng"""
    customer_id = data.get('customer_id')
    db = get_db_connection()
    cursor = db.cursor()
    try:
        sql = """
            UPDATE Customer 
            SET name = %s, phonenum = %s, email = %s, customer_type = %s 
            WHERE customer_id = %s
        """
        cursor.execute(sql, (data.get('name'), data.get('phone'), 
                             data.get('email'), data.get('customer_type'), customer_id))
        db.commit()
        return True, f"Cập nhật khách hàng {customer_id} thành công!"
    except Exception as e:
        db.rollback()
        return False, f"Lỗi: {str(e)}"
    finally:
        cursor.close()
        db.close()

def delete_customer_action(customer_id):
    """Xóa khách hàng"""
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM Customer WHERE customer_id = %s", (customer_id,))
        db.commit()
        return True, "Đã xóa khách hàng khỏi hệ thống!"
    except Exception:
        db.rollback()
        # Lỗi thường do khách hàng đã có lịch sử đặt vé (khóa ngoại)
        return False, "Không thể xóa khách hàng này vì đã có lịch sử đặt vé!"
    finally:
        cursor.close()
        db.close()