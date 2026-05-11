from back_end.admin_queries import get_db_connection

def add_trip_action(data):
    trip_id = data.get('trip_id')
    dep_time = f"{data.get('departure_date')} {data.get('departure_time')}:00"
    
    db = get_db_connection()
    cursor = db.cursor()
    try:
        # SỬA: Xóa capacity, thêm license_plate
        sql = """
            INSERT INTO Trip (trip_id, dep_time, price, dep_sta_id, arr_sta_id, license_plate, type)
            VALUES (%s, %s, %s, %s, %s, %s, 'normal')
        """
        cursor.execute(sql, (trip_id, dep_time, data.get('price'), 
                             data.get('start_point'), data.get('end_point'), data.get('license_plate')))
        db.commit()
        return True, f"Thêm chuyến {trip_id} thành công!"
    except Exception as e:
        db.rollback()
        return False, f"Lỗi SQL: {str(e)}"
    finally:
        cursor.close()
        db.close()

def edit_trip_action(data):
    trip_id = data.get('trip_id')
    dep_time = f"{data.get('departure_date')} {data.get('departure_time')}:00"
    
    db = get_db_connection()
    cursor = db.cursor()
    try:
        # SỬA: Cập nhật license_plate thay vì capacity
        sql = """
            UPDATE Trip 
            SET dep_time = %s, price = %s, dep_sta_id = %s, arr_sta_id = %s, license_plate = %s
            WHERE trip_id = %s
        """
        cursor.execute(sql, (dep_time, data.get('price'), data.get('start_point'), 
                             data.get('end_point'), data.get('license_plate'), trip_id))
        db.commit()
        return True, f"Cập nhật {trip_id} thành công!"
    except Exception as e:
        db.rollback()
        return False, f"Lỗi: {str(e)}"
    finally:
        cursor.close()
        db.close()

def delete_trip_action(trip_id):
    """Xử lý xóa chuyến xe"""
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM Trip WHERE trip_id = %s", (trip_id,))
        db.commit()
        return True, "Xóa chuyến xe thành công!"
    except Exception:
        db.rollback()
        return False, "Không thể xóa vì chuyến xe đã có khách đặt vé!"
    finally:
        cursor.close()
        db.close()