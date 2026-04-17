from flask import Flask, render_template, request
import mysql.connector

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

    # Lấy tham số lọc từ URL (ví dụ: /trip_list?diem_di=Hà Nội&diem_den=Hà Tĩnh&ngay_di=20/04/2026)
    diem_di  = request.args.get('diem_di', '').strip()
    diem_den = request.args.get('diem_den', '').strip()
    ngay_di  = request.args.get('ngay_di', '').strip()

    # Lấy danh sách tỉnh cho dropdown
    cursor.execute("SELECT DISTINCT province FROM Location ORDER BY province")
    provinces = cursor.fetchall()

    # Chuyển ngày từ định dạng dd/mm/yyyy → yyyy-mm-dd cho MySQL
    ngay_di_sql = None
    if ngay_di:
        try:
            from datetime import datetime
            ngay_di_sql = datetime.strptime(ngay_di, '%d/%m/%Y').strftime('%Y-%m-%d')
        except ValueError:
            ngay_di_sql = None

    # Query chuyến xe với filter
    sql = """
        SELECT
            t.trip_id,
            t.dep_time,
            t.arr_time,
            t.duration,
            t.type,
            t.price,
            t.license_plate,
            dep_loc.station  AS dep_station,
            dep_loc.province AS dep_province,
            arr_loc.station  AS arr_station,
            arr_loc.province AS arr_province,
            b.capacity,
            -- Đếm số ghế đã bán (số Ticket_Seat của chuyến này)
            (SELECT COUNT(*)
             FROM Ticket_Seat ts
             JOIN Ticket tk ON ts.tic_id = tk.tic_id
             WHERE tk.trip_id = t.trip_id
            ) AS sold_seats
        FROM Trip t
        JOIN Location dep_loc ON t.dep_sta_id = dep_loc.loc_id
        JOIN Location arr_loc ON t.arr_sta_id = arr_loc.loc_id
        JOIN Bus b ON t.license_plate = b.license_plate
        WHERE 1=1
    """
    params = []

    if diem_di:
        sql += " AND dep_loc.province = %s"
        params.append(diem_di)
    if diem_den:
        sql += " AND arr_loc.province = %s"
        params.append(diem_den)
    if ngay_di_sql:
        sql += " AND DATE(t.dep_time) = %s"
        params.append(ngay_di_sql)

    sql += " ORDER BY t.dep_time ASC"

    cursor.execute(sql, params)
    trips = cursor.fetchall()

    # Tính ghế còn trống cho từng chuyến
    for trip in trips:
        trip['free_seats'] = trip['capacity'] - trip['sold_seats']

    cursor.close()
    db.close()

    return render_template(
        'trip_list.html',
        trips=trips,
        provinces=provinces,
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
