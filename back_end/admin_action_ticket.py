from back_end.admin_queries import get_db_connection

def cancel_ticket_action(bill_id):
    db = get_db_connection()
    cursor = db.cursor()
    try:
        # Cập nhật trạng thái thành 'Đã hủy' để giữ lại lịch sử hóa đơn
        cursor.execute("UPDATE Bill SET status = 'Đã hủy' WHERE bill_id = %s", (bill_id,))
        db.commit()
        return True, f"Đã hủy hóa đơn {bill_id} thành công!"
    except Exception as e:
        db.rollback()
        return False, f"Lỗi: {str(e)}"
    finally:
        cursor.close()
        db.close()