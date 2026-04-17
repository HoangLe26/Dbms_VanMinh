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

    sql = """
        SELECT
            t.trip_id, t.dep_time, t.arr_time, t.duration, t.type, t.price, t.license_plate,
            dep_loc.station  AS dep_station, dep_loc.province AS dep_province,
            arr_loc.station  AS arr_station, arr_loc.province AS arr_province,
            b.capacity,
            (SELECT COUNT(*) FROM Ticket_Seat ts JOIN Ticket tk ON ts.tic_id = tk.tic_id WHERE tk.trip_id = t.trip_id) AS sold_seats
        FROM Trip t
        JOIN Location dep_loc ON t.dep_sta_id = dep_loc.loc_id
        JOIN Location arr_loc ON t.arr_sta_id = arr_loc.loc_id
        JOIN Bus b ON t.license_plate = b.license_plate
        WHERE 1=1
    """
    params = []

    if ngay_di_sql:
        sql += " AND DATE(t.dep_time) = %s"
        params.append(ngay_di_sql)

    sql += " ORDER BY t.dep_time ASC"

    cursor.execute(sql, params)
    trips = cursor.fetchall()

    # 2. GỌT SẠCH DATA CHUYẾN XE TRƯỚC KHI SO SÁNH
    for trip in trips:
        trip['free_seats'] = trip['capacity'] - trip['sold_seats']
        # Gọt sạch ký tự thừa ở tỉnh đi và tỉnh đến
        if trip['dep_province']: trip['dep_province'] = trip['dep_province'].strip()
        if trip['arr_province']: trip['arr_province'] = trip['arr_province'].strip()

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

if __name__ == '__main__':
    app.run(debug=True)
