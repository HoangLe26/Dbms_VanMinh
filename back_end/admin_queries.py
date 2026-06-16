import mysql.connector
from datetime import date

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root", 
        password="2609", 
        database="dbms_vanminh"
    )

def get_dashboard_stats():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    stats = {}
    try:
        # Lấy doanh thu
        cursor.execute("SELECT SUM(total) as total FROM Bill WHERE status = 'Đã thanh toán'")
        res = cursor.fetchone()
        stats['revenue'] = res['total'] if res['total'] else 0

        cursor.execute("SELECT COUNT(*) as total FROM Bill")
        stats['tickets'] = cursor.fetchone()['total']

        cursor.execute("SELECT COUNT(*) as total FROM Trip WHERE DATE(dep_time) = %s", (date.today(),))
        stats['trips_today'] = cursor.fetchone()['total']

        cursor.execute("SELECT COUNT(*) as total FROM Customer WHERE username NOT LIKE 'admin%'")
        stats['customers'] = cursor.fetchone()['total']
        
        # Thêm ngày hiện tại để header admin.html không bị trống
        stats['current_date'] = date.today().strftime('%d/%m/%Y')
        return stats
    finally:
        cursor.close()
        db.close()

def get_all_tickets():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        # SỬA: Dùng LEFT JOIN cho Customer để tránh mất dữ liệu nếu ID chưa khớp
        # SỬA: Bổ sung đầy đủ cột vào GROUP BY để tránh lỗi SQL
        # SỬA: Dùng %H:%i (1 dấu %) vì không có tham số %s trong câu query này
        query = """
            SELECT 
                b.bill_id as ticket_id, 
                IFNULL(c.name, 'Khách vãng lai') as customer_name, 
                IFNULL(c.phonenum, 'N/A') as phone, 
                CONCAT(IFNULL(l1.province, t.dep_sta_id), ' -> ', IFNULL(l2.province, t.arr_sta_id)) as route,
                DATE_FORMAT(t.dep_time, '%H:%i | %d/%m/%Y') as time,
                DATE_FORMAT(b.date, '%d/%m/%Y %H:%i') as booking_date, 
                b.status,
                GROUP_CONCAT(DISTINCT s.seat_code SEPARATOR ', ') as seat_no
            FROM Bill b
            LEFT JOIN Customer c ON b.customer_id = c.customer_id
            LEFT JOIN Ticket tk ON b.bill_id = tk.bill_id
            LEFT JOIN Trip t ON tk.trip_id = t.trip_id
            LEFT JOIN Ticket_Seat ts ON tk.tic_id = ts.tic_id
            LEFT JOIN Seat s ON ts.seat_id = s.seat_id
            LEFT JOIN Location l1 ON t.dep_sta_id = l1.loc_id
            LEFT JOIN Location l2 ON t.arr_sta_id = l2.loc_id
            GROUP BY 
                b.bill_id, c.name, c.phonenum, 
                l1.province, t.dep_sta_id, l2.province, t.arr_sta_id, 
                t.dep_time, b.date, b.status
            ORDER BY b.date DESC
        """
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        print(f"Lỗi SQL tại get_all_tickets: {e}")
        return []
    finally:
        cursor.close()
        db.close()
def get_ticket_details(bill_id):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        query = """
            SELECT 
                b.bill_id, b.total, b.method, b.status,
                DATE_FORMAT(b.date, '%d/%m/%Y %H:%i') as booking_date, -- Đổi %% thành %
                c.name as customer_name, c.phonenum, c.email, c.customer_type,
                t.trip_id, t.license_plate,
                DATE_FORMAT(t.dep_time, '%H:%i | %d/%m/%Y') as dep_time, -- Đổi %% thành %
                l1.province as dep_prov, l1.station as dep_sta,
                l2.province as arr_prov, l2.station as arr_sta,
                GROUP_CONCAT(DISTINCT s.seat_code SEPARATOR ', ') as seats
            FROM Bill b
            JOIN Customer c ON b.customer_id = c.customer_id
            LEFT JOIN Ticket tk ON b.bill_id = tk.bill_id
            LEFT JOIN Trip t ON tk.trip_id = t.trip_id
            LEFT JOIN Location l1 ON t.dep_sta_id = l1.loc_id
            LEFT JOIN Location l2 ON t.arr_sta_id = l2.loc_id
            LEFT JOIN Ticket_Seat ts ON tk.tic_id = ts.tic_id
            LEFT JOIN Seat s ON ts.seat_id = s.seat_id
            WHERE b.bill_id = %s
            GROUP BY 
                b.bill_id, b.total, b.method, b.status, b.date,
                c.name, c.phonenum, c.email, c.customer_type,
                t.trip_id, t.license_plate, t.dep_time,
                l1.province, l1.station, l2.province, l2.station
        """
        cursor.execute(query, (bill_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        db.close()

def get_customer_stats():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT COUNT(*) as total FROM Customer WHERE username NOT LIKE 'admin%'")
        total = cursor.fetchone()['total']
        
        # Khớp hạng 'special' theo DB
        cursor.execute("SELECT COUNT(*) as special_count FROM Customer WHERE LOWER(customer_type) = 'special'")
        special_count = cursor.fetchone()['special_count']
        
        return {'total': total, 'special_count': special_count}
    finally:
        cursor.close()
        db.close()

def get_all_trips():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        # BỔ SUNG: Lấy thêm dep_sta_id, arr_sta_id và license_plate để JS dùng
        query = """
            SELECT 
                t.trip_id, t.dep_sta_id, t.arr_sta_id, t.license_plate, t.type,
                IFNULL(l1.province, t.dep_sta_id) as start_point, 
                IFNULL(l2.province, t.arr_sta_id) as end_point, 
                DATE(t.dep_time) as departure_date, 
                TIME(t.dep_time) as departure_time, 
                t.price 
            FROM Trip t
            LEFT JOIN Location l1 ON t.dep_sta_id = l1.loc_id
            LEFT JOIN Location l2 ON t.arr_sta_id = l2.loc_id
            ORDER BY t.dep_time DESC
        """
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        cursor.close()
        db.close()

def get_all_customers():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        query = "SELECT * FROM Customer WHERE username NOT LIKE 'admin%' ORDER BY name ASC"
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        cursor.close()
        db.close()

def get_all_buses():
    """Lấy danh sách tất cả các xe"""
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT license_plate, bus_description FROM bus")
        return cursor.fetchall()
    finally:
        cursor.close()
        db.close()

def get_all_locations():
    """Lấy danh sách tất cả các bến xe"""
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT loc_id, station, province FROM location")
        return cursor.fetchall()
    finally:
        cursor.close()
        db.close()

def get_revenue_by_month():
    """Lấy thống kê doanh thu theo từng tháng từ vw_Revenue_By_Month."""
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        # Lấy 6 tháng gần nhất để hiển thị lên Dashboard
        cursor.execute("SELECT * FROM vw_Revenue_By_Month LIMIT 6")
        return cursor.fetchall()
    except Exception as e:
        print(f"Lỗi SQL tại get_revenue_by_month: {e}")
        return []
    finally:
        cursor.close()
        db.close()

def get_top_routes():
    """Lấy Top 3 tuyến xe bán chạy nhất từ vw_Top_Routes."""
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        # Chỉ lấy Top 3
        cursor.execute("SELECT * FROM vw_Top_Routes LIMIT 3")
        return cursor.fetchall()
    except Exception as e:
        print(f"Lỗi SQL tại get_top_routes: {e}")
        return []
    finally:
        cursor.close()
        db.close()