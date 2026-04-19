from flask import Flask, render_template, request
import mysql.connector
import unicodedata

app = Flask(__name__, static_folder='assets', static_url_path='/assets')

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root", 
        password="2609", 
        database="dbms_vanminh"
    )

# ───── Trang chủ ─────
@app.route('/')
def home():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT DISTINCT province FROM Location ORDER BY province")
    danh_sach_tinh = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('index.html', provinces=danh_sach_tinh)


# ───── Danh sách chuyến xe ─────
@app.route('/trip_list')
def trip_list():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Lấy tham số lọc từ URL
    diem_di  = unicodedata.normalize('NFC', request.args.get('diem_di', '').strip())
    diem_den = unicodedata.normalize('NFC', request.args.get('diem_den', '').strip())
    ngay_di  = request.args.get('ngay_di', '').strip()

    # 1. LẤY VÀ GỌT SẠCH DANH SÁCH TỈNH CHO DROPDOWN
    cursor.execute("SELECT DISTINCT province FROM Location ORDER BY province")
    provinces_raw = cursor.fetchall()
    # Thêm .strip() để gọt sạch khoảng trắng/ký tự ẩn từ Database
    provinces = [{'province': unicodedata.normalize('NFC', p['province']).strip()} for p in provinces_raw]
    
    # Loại bỏ các tỉnh bị trùng lặp sau khi đã gọt sạch khoảng trắng
    seen = set()
    clean_provinces = []
    for p in provinces:
        if p['province'] not in seen and p['province'] != "":
            seen.add(p['province'])
            clean_provinces.append(p)

    # Chuyển ngày
    ngay_di_sql = None
    if ngay_di:
        try:
            from datetime import datetime
            ngay_di_sql = datetime.strptime(ngay_di, '%d/%m/%Y').strftime('%Y-%m-%d')
        except ValueError:
            ngay_di_sql = None

    # Bổ sung dòng GROUP_CONCAT vào câu query
    # Query chuyến xe với filter (Đã bổ sung GROUP_CONCAT)
    sql = """
        SELECT
            t.trip_id, t.dep_time, t.arr_time, t.duration, t.type, t.price, t.license_plate,
            dep_loc.station  AS dep_station, dep_loc.province AS dep_province,
            arr_loc.station  AS arr_station, arr_loc.province AS arr_province,
            b.capacity,
            (SELECT COUNT(*) FROM Ticket_Seat ts JOIN Ticket tk ON ts.tic_id = tk.tic_id WHERE tk.trip_id = t.trip_id) AS sold_seats,
            (SELECT GROUP_CONCAT(s.seat_code) FROM Ticket_Seat ts JOIN Ticket tk ON ts.tic_id = tk.tic_id JOIN Seat s ON ts.seat_id = s.seat_id WHERE tk.trip_id = t.trip_id) AS booked_seats_str
        FROM Trip t
        JOIN Location dep_loc ON t.dep_sta_id = dep_loc.loc_id
        JOIN Location arr_loc ON t.arr_sta_id = arr_loc.loc_id
        JOIN Bus b ON t.license_plate = b.license_plate
        WHERE 1=1
    """
    
    # DÒNG NÀY RẤT QUAN TRỌNG ĐỂ KHÔNG BỊ LỖI
    params = [] 

    # Chỉ giữ filter ngày trong SQL
    if ngay_di_sql:
        sql += " AND DATE(t.dep_time) = %s"
        params.append(ngay_di_sql)

    sql += " ORDER BY t.dep_time ASC"

    cursor.execute(sql, params)
    trips = cursor.fetchall()

    # 2. GỌT SẠCH DATA CHUYẾN XE VÀ XỬ LÝ GHẾ
    for trip in trips:
        trip['free_seats'] = trip['capacity'] - trip['sold_seats']
        
        # Gọt sạch ký tự thừa ở tỉnh đi và tỉnh đến
        if trip['dep_province']: trip['dep_province'] = trip['dep_province'].strip()
        if trip['arr_province']: trip['arr_province'] = trip['arr_province'].strip()
        
        # --- ĐÂY CHÍNH LÀ ĐOẠN BỊ THIẾU ---
        # Biến chuỗi "A1,A2" từ SQL thành một danh sách ['A1', 'A2'] để HTML đọc được
        if trip['booked_seats_str']:
            # split(',') để tách chuỗi, strip() để dọn dẹp ký tự tàng hình nếu có
            trip['booked_seats'] = [s.strip() for s in trip['booked_seats_str'].split(',')]
        else:
            trip['booked_seats'] = []

    # 3. LỌC CHÍNH XÁC 100%
    if diem_di:
        nfc_di = unicodedata.normalize('NFC', diem_di)
        trips = [t for t in trips if unicodedata.normalize('NFC', t['dep_province']) == nfc_di]
        
    if diem_den:
        nfc_den = unicodedata.normalize('NFC', diem_den)
        trips = [t for t in trips if unicodedata.normalize('NFC', t['arr_province']) == nfc_den]

    cursor.close()
    db.close()

    return render_template(
        'trip_list.html',
        trips=trips,
        provinces=clean_provinces, # Truyền danh sách tỉnh siêu sạch ra giao diện
        diem_di=diem_di,
        diem_den=diem_den,
        ngay_di=ngay_di,
        total=len(trips)
    )

# ───── Admin Dashboard ─────
@app.route('/admin')
def admin_dashboard():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # 1. KPIs
    cursor.execute("SELECT SUM(total) AS total_revenue FROM Bill")
    total_revenue = cursor.fetchone()['total_revenue'] or 0

    cursor.execute("SELECT COUNT(*) AS total_customers FROM Customer")
    total_customers = cursor.fetchone()['total_customers'] or 0

    cursor.execute("SELECT COUNT(*) AS total_tickets FROM Ticket")
    total_tickets = cursor.fetchone()['total_tickets'] or 0

    cursor.execute("SELECT COUNT(*) AS total_trips FROM Trip")
    total_trips = cursor.fetchone()['total_trips'] or 0

    kpis = {
        'revenue': total_revenue,
        'customers': total_customers,
        'tickets': total_tickets,
        'trips': total_trips
    }

    # 2. Revenue by Payment Method
    cursor.execute("SELECT method, COUNT(*) as count FROM Bill GROUP BY method")
    payment_methods = cursor.fetchall()

    # 3. Top 5 Popular Routes
    cursor.execute("""
        SELECT dep_loc.province AS dep, arr_loc.province AS arr, COUNT(tk.tic_id) AS ticket_count 
        FROM Ticket tk 
        JOIN Trip t ON tk.trip_id = t.trip_id 
        JOIN Location dep_loc ON t.dep_sta_id = dep_loc.loc_id 
        JOIN Location arr_loc ON t.arr_sta_id = arr_loc.loc_id 
        GROUP BY dep_loc.province, arr_loc.province 
        ORDER BY ticket_count DESC 
        LIMIT 5
    """)
    popular_routes = cursor.fetchall()

    # 4. Top 5 Customers
    cursor.execute("""
        SELECT c.name, c.phonenum, SUM(b.total) as total_spent 
        FROM Bill b 
        JOIN Customer c ON b.customer_id = c.customer_id 
        GROUP BY c.customer_id, c.name, c.phonenum 
        ORDER BY total_spent DESC 
        LIMIT 5
    """)
    top_customers = cursor.fetchall()

    # 5. Revenue Over Time (Daily)
    cursor.execute("""
        SELECT DATE(date) as bill_date, SUM(total) as daily_revenue 
        FROM Bill 
        GROUP BY DATE(date) 
        ORDER BY bill_date
    """)
    revenue_daily = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('admin_dashboard.html', 
                           kpis=kpis, 
                           payment_methods=payment_methods,
                           popular_routes=popular_routes,
                           top_customers=top_customers,
                           revenue_daily=revenue_daily)

# ───── Quản lý Khách hàng ─────
@app.route('/admin/customers')
def admin_customers():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Lấy danh sách khách hàng và tổng tiền họ đã chi tiêu
    cursor.execute("""
        SELECT c.customer_id, c.name, c.phonenum, c.email, c.customer_type, 
               COALESCE(SUM(b.total), 0) as total_spent,
               COUNT(b.bill_id) as total_orders
        FROM Customer c
        LEFT JOIN Bill b ON c.customer_id = b.customer_id
        GROUP BY c.customer_id, c.name, c.phonenum, c.email, c.customer_type
        ORDER BY total_spent DESC
    """)
    customers = cursor.fetchall()
    
    # KPIs
    cursor.execute("SELECT COUNT(*) as total FROM Customer")
    total_customers = cursor.fetchone()['total'] or 0
    
    cursor.execute("SELECT COUNT(*) as vip FROM Customer WHERE customer_type = 'special'")
    vip_customers = cursor.fetchone()['vip'] or 0

    cursor.close()
    db.close()
    
    return render_template('admin_customers.html', customers=customers, total_customers=total_customers, vip_customers=vip_customers)

# ───── Quản lý Vé & Hóa đơn ─────
@app.route('/admin/tickets')
def admin_tickets():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Lấy danh sách hóa đơn
    cursor.execute("""
        SELECT b.bill_id, c.name as customer_name, b.date, b.total, b.method, b.status
        FROM Bill b
        LEFT JOIN Customer c ON b.customer_id = c.customer_id
        ORDER BY b.date DESC
    """)
    bills = cursor.fetchall()
    
    # KPIs
    cursor.execute("SELECT COUNT(*) as total_bills, SUM(total) as total_revenue FROM Bill")
    kpi_data = cursor.fetchone()
    total_bills = kpi_data['total_bills'] or 0
    total_revenue = kpi_data['total_revenue'] or 0

    cursor.close()
    db.close()
    
    return render_template('admin_tickets.html', bills=bills, total_bills=total_bills, total_revenue=total_revenue)

# ───── Tra cứu vé ─────
@app.route('/tra_cuu')
def tra_cuu():
    return render_template('tra_cuu.html')

# ───── Giới thiệu ─────
@app.route('/gioi_thieu')
def gioi_thieu():
    return render_template('gioi_thieu.html')

@app.route('/co_cau_to_chuc')
def co_cau_to_chuc():
    return render_template('co_cau_to_chuc.html')

# ───── Chính sách ─────
@app.route('/chinh_sach_bao_mat')
def chinh_sach_bao_mat():
    return render_template('chinh_sach_bao_mat.html')

@app.route('/chinh_sach_thanh_toan')
def chinh_sach_thanh_toan():
    return render_template('chinh_sach_thanh_toan.html')

# ───── Điều khoản ─────
@app.route('/dieu_khoan_van_minh')
def dieu_khoan_van_minh():
    return render_template('dieu_khoan_van_minh.html')

# ───── Liên hệ ─────
@app.route('/lien_he')
def lien_he():
    return render_template('lien_he.html')

# ───── Thanh toán ─────
@app.route('/payment')
def payment():
    price = request.args.get('price', '0')
    unit_price = request.args.get('unit_price', '0')
    try:
        price_str = f"{int(price):,}".replace(',', '.') + ' đ'
        unit_price_str = f"{int(unit_price):,}".replace(',', '.') + ' đ'
    except ValueError:
        price_str = price + ' đ'
        unit_price_str = unit_price + ' đ'
        
    phone = request.args.get('phone', '')
    name = request.args.get('name', '')
    seats = request.args.get('seats', '')
    seat_list = seats.split(',') if seats else []
    
    dep_prov = request.args.get('dep_prov', '')
    dep_sta = request.args.get('dep_sta', '')
    arr_prov = request.args.get('arr_prov', '')
    arr_sta = request.args.get('arr_sta', '')
    bus_type = request.args.get('type', '')
    time = request.args.get('time', '')
    
    return render_template('payment.html', 
                           price=price_str, unit_price=unit_price_str,
                           phone=phone, name=name, seats=seats, seat_list=seat_list,
                           dep_prov=dep_prov, dep_sta=dep_sta, 
                           arr_prov=arr_prov, arr_sta=arr_sta, 
                           bus_type=bus_type, time=time)



@app.route('/api/lock_seats', methods=['POST'])
def lock_seats():
    data = request.get_json()
    db = get_db_connection()
    cursor = db.cursor()
    try:
        # 1. Tạo mã Bill duy nhất
        import time
        bill_id = f"BILL_{int(time.time())}"
        
        # 2. Chèn hóa đơn với trạng thái 'Đang chờ'
        # Lưu ý: Tên cột 'total' và 'date' khớp với file app.py của bạn
        sql_bill = "INSERT INTO Bill (bill_id, total, method, status, date, customer_id) VALUES (%s, %s, %s, %s, NOW(), %s)"
        cursor.execute(sql_bill, (bill_id, data['total_price'], 'QR', 'Đang chờ', 'CUS_001'))
        # 3. Chèn vào bảng Ticket và Ticket_Seat cho TỪNG ghế
        unit_price = data['total_price'] / len(data['seats'])
        
        sql_tic = "INSERT INTO Ticket (tic_id, price, trip_id, bill_id) VALUES (%s, %s, %s, %s)"
        sql_seat = "INSERT INTO Ticket_Seat (tic_id, seat_id) VALUES (%s, (SELECT seat_id FROM Seat WHERE TRIM(seat_code) = TRIM(%s) LIMIT 1))"
        
        for index, seat_code in enumerate(data['seats']):
            # Tạo tic_id sao cho không bị trùng (dùng time + index)
            tic_id = f"TIC_{int(time.time())}{index}"
            
            # Chèn Ticket (nhớ truyền unit_price vào cho cột price)
            cursor.execute(sql_tic, (tic_id, unit_price, data['trip_id'], bill_id))
            
            # Chèn Ticket_Seat
            cursor.execute(sql_seat, (tic_id, seat_code))

        db.commit()
        return jsonify({"success": True, "bill_id": bill_id})
    except Exception as e:
        db.rollback()
        return jsonify({"success": False, "error": str(e)})
    finally:
        cursor.close()
        db.close()

# ───── API Xác nhận thanh toán ─────
from flask import jsonify
@app.route('/api/confirm_payment', methods=['POST'])
def confirm_payment():
    data = request.get_json()
    db = get_db_connection()
    cursor = db.cursor()
    try:
        # Cập nhật trạng thái thành 'Đã thanh toán'
        sql = "UPDATE Bill SET status = 'Đã thanh toán' WHERE bill_id = %s"
        cursor.execute(sql, (data['bill_id'],))
        db.commit()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    finally:
        cursor.close()
        db.close()

if __name__ == '__main__':
    app.run(debug=True)
