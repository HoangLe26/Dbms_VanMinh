from flask import Flask, render_template, request, session, redirect, url_for, flash, jsonify
from mysql.connector import pooling
import mysql.connector
import unicodedata
from back_end.check_login import verify_account, init_pool
from back_end.admin_queries import get_all_trips, get_all_tickets, get_all_customers, get_dashboard_stats
from back_end.admin_action_trip import add_trip_action, edit_trip_action, delete_trip_action
from back_end.admin_action_ticket import cancel_ticket_action
from back_end.admin_action_customer import edit_customer_action, delete_customer_action

app = Flask(__name__, static_folder='assets', static_url_path='/assets')
app.secret_key = 'vanminh_secret_key_2026'

# ───── CONNECTION POOL (Buffer tối ưu kết nối DB) ─────
# Thay vì tạo kết nối mới mỗi request, pool giữ sẵn 5 kết nối trong RAM.
# Khi có request -> lấy kết nối có sẵn -> trả lại pool sau khi xong.
_db_pool = pooling.MySQLConnectionPool(
    pool_name="vanminh_pool",
    pool_size=5,          # Giữ sẵn tối đa 5 kết nối đồng thời
    pool_reset_session=True,
    host="localhost",
    user="root",
    password="2609",
    database="dbms_vanminh"
)

def get_db_connection():
    """Lấy một kết nối từ pool (không tạo mới)."""
    return _db_pool.get_connection()

# Chia sẻ pool với module check_login để dùng chung, không tạo kết nối riêng
init_pool(_db_pool)

# ───── APP CACHE (Buffer tối ưu dữ liệu ít thay đổi) ─────
# Danh sách tỉnh hầu như không đổi -> cache lại, không query DB mỗi lần.
_cache_provinces = None

def get_provinces_cached():
    """Trả về danh sách tỉnh từ cache. Chỉ query DB lần đầu tiên."""
    global _cache_provinces
    if _cache_provinces is None:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT DISTINCT province FROM Location ORDER BY province")
        raw = cursor.fetchall()
        cursor.close()
        db.close()
        # Gọt sạch và lọc trùng
        seen = set()
        result = []
        for p in raw:
            name = unicodedata.normalize('NFC', p['province']).strip()
            if name and name not in seen:
                seen.add(name)
                result.append({'province': name})
        _cache_provinces = result
    return _cache_provinces

# ───── Start Login ─────

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_name' in session:
        return redirect(url_for('home'))
        
    # xử lí bấm nút login
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Gọi file check_login
        success, user = verify_account(username, password)

        if success:
            # Lưu thông tin chung
            session['user_name'] = user['name']
            session['user_id'] = user['customer_id']
            
            # --- BẮT ĐẦU KIỂM TRA TIỀN TỐ ADMIN ---
            # Chuyển username về chữ thường và kiểm tra có bắt đầu bằng 'admin' không
            if username.lower().startswith('admin'):
                session['role'] = 'admin' # Lưu thêm cờ admin
                return redirect(url_for('admin')) # Chuyển hướng sang trang quản trị
            else:
                session['role'] = 'customer'
                return redirect(url_for('home')) # Chuyển hướng sang trang chủ khách hàng
            # --- KẾT THÚC KIỂM TRA ---
            
        else:
            # Sai mật khẩu -> Báo lỗi và bắt nhập lại
            flash("Tên đăng nhập hoặc mật khẩu không chính xác!")
            return redirect(url_for('login'))

    # Nếu truy cập bình thường (GET) thì hiện form giao diện lên
    return render_template('login.html')

# ───── End Login ─────



## ───── Start logout ─────
@app.route('/logout')
def logout():
    session.clear() # Xóa sạch "thẻ" người dùng
    # Quan trọng: Chuyển hướng thẳng về trang login thay vì home
    return redirect(url_for('login'))
# ───── End Logout ─────

# ───── Start Register ─────
@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_name' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        fullname = request.form.get('fullname', '').strip()
        phone    = request.form.get('phone', '').strip()
        email    = request.form.get('email', '').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        # --- BẮT ĐẦU CHỐT CHẶN BẢO MẬT ---
        if username.lower().startswith('admin'):
            flash("Lỗi: Tên đăng nhập không được chứa từ khóa quản trị hệ thống!", "error")
            return redirect(url_for('register'))
        # --- KẾT THÚC CHỐT CHẶN ---

        # ── Validate bắt buộc ──
        if not fullname:
            flash('Vui lòng nhập họ và tên!', 'error')
            return render_template('register.html', form_data=request.form)

        if not phone:
            flash('Vui lòng nhập số điện thoại!', 'error')
            return render_template('register.html', form_data=request.form)

        # ── Validate username & password đi cùng nhau ──
        if username and not password:
            flash('Vui lòng nhập mật khẩu khi sử dụng tên đăng nhập!', 'error')
            return render_template('register.html', form_data=request.form)

        if password and not username:
            flash('Vui lòng nhập tên đăng nhập khi sử dụng mật khẩu!', 'error')
            return render_template('register.html', form_data=request.form)

        if password and len(password) < 6:
            flash('Mật khẩu phải có ít nhất 6 ký tự!', 'error')
            return render_template('register.html', form_data=request.form)

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        try:
            # Kiểm tra số điện thoại đã tồn tại chưa
            cursor.execute("SELECT customer_id FROM Customer WHERE phonenum = %s LIMIT 1", (phone,))
            if cursor.fetchone():
                flash('Số điện thoại này đã được đăng ký!', 'error')
                return render_template('register.html', form_data=request.form)

            # Kiểm tra tên đăng nhập đã tồn tại chưa (nếu có nhập)
            if username:
                cursor.execute("SELECT customer_id FROM Customer WHERE username = %s LIMIT 1", (username,))
                if cursor.fetchone():
                    flash('Tên đăng nhập này đã được sử dụng, vui lòng chọn tên khác!', 'error')
                    return render_template('register.html', form_data=request.form)

            # Tạo customer_id mới
            import time as _time
            customer_id = f"CUS_{int(_time.time())}"

            # Chèn khách hàng mới vào DB
            sql = """
                INSERT INTO Customer (customer_id, name, phonenum, email, username, password, customer_type)
                VALUES (%s, %s, %s, %s, %s, %s, 'normal')
            """
            cursor.execute(sql, (
                customer_id,
                fullname,
                phone,
                email if email else None,
                username if username else None,
                password if password else None
            ))
            db.commit()

            flash('Đăng ký thành công! Vui lòng đăng nhập.', 'success')
            return redirect(url_for('login'))

        except Exception as e:
            db.rollback()
            flash(f'Lỗi hệ thống: {str(e)}', 'error')
            return render_template('register.html', form_data=request.form)
        finally:
            cursor.close()
            db.close()

    return render_template('register.html')
# ───── End Register ─────

# ───── Trang Quản trị (Admin) ─────
@app.route('/admin')
def admin():
    # Kiểm tra bảo mật: Bắt buộc phải đăng nhập VÀ có quyền admin
    if 'user_name' in session and session.get('role') == 'admin':
        
        # 1. Lấy các con số thống kê (Doanh thu, Vé, Khách...) từ DB
        stats_data = get_dashboard_stats()
        
        # 2. Lấy danh sách chuyến xe (lấy 5 chuyến mới nhất để hiện ở bảng)
        all_trips = get_all_trips()
        trips_data = all_trips[:5] if all_trips else []
        
        # 3. Truyền các biến stats và trips vào template
        return render_template('admin.html', stats=stats_data, trips=trips_data)
        
    else:
        flash("Bạn không có quyền truy cập trang quản trị hệ thống!", "error")
        return redirect(url_for('login'))

# START TRIP
@app.route('/admin_trips')
@app.route('/admin_trips')
def admin_trips():
    if 'user_name' in session and session.get('role') == 'admin':
        from back_end.admin_queries import get_all_trips, get_all_buses, get_all_locations
        data = get_all_trips()
        buses_list = get_all_buses()        # Lấy danh sách xe
        locations_list = get_all_locations() # Lấy danh sách bến
        return render_template('admin_trips.html', 
                               trips=data, 
                               buses=buses_list, 
                               locations=locations_list)
    return redirect(url_for('login'))
@app.route('/add_trip', methods=['POST'])
def add_trip():
    if 'user_name' in session and session.get('role') == 'admin':
        success, message = add_trip_action(request.form)
        flash(message, "success" if success else "error")
        return redirect(url_for('admin_trips'))
    return redirect(url_for('login'))

@app.route('/edit_trip', methods=['POST'])
def edit_trip():
    if 'user_name' in session and session.get('role') == 'admin':
        success, message = edit_trip_action(request.form)
        flash(message, "success" if success else "error")
        return redirect(url_for('admin_trips'))
    return redirect(url_for('login'))
@app.route('/delete_trip/<trip_id>')
def delete_trip(trip_id):
    if 'user_name' in session and session.get('role') == 'admin':
        success, message = delete_trip_action(trip_id)
        flash(message, "success" if success else "error")
        return redirect(url_for('admin_trips'))
    return redirect(url_for('login'))
# END TRIP

# START TICKET
@app.route('/admin_tickets')
def admin_tickets():
    if 'user_name' in session and session.get('role') == 'admin':
        data = get_all_tickets() # Gọi hàm từ file admin_queries
        return render_template('admin_tickets.html', tickets=data)
    return redirect(url_for('login'))
@app.route('/api/ticket_details/<bill_id>')
def ticket_details_api(bill_id):
    if 'user_name' in session and session.get('role') == 'admin':
        from back_end.admin_queries import get_ticket_details
        details = get_ticket_details(bill_id)
        if details:
            return jsonify(details)
        return jsonify({"error": "Không tìm thấy vé"}), 404
    return jsonify({"error": "Unauthorized"}), 401
@app.route('/admin/cancel_ticket/<bill_id>')
def admin_cancel_ticket(bill_id): # Đổi tên hàm để tránh lỗi Method Not Allowed
    if 'user_name' in session and session.get('role') == 'admin':
        success, message = cancel_ticket_action(bill_id)
        flash(message, "success" if success else "error")
        return redirect(url_for('admin_tickets'))
    return redirect(url_for('login'))
# END TICKET

# START CUSTOMER
@app.route('/admin_customers')
def admin_customers():
    if 'user_name' in session and session.get('role') == 'admin':
        from back_end.admin_queries import get_all_customers, get_customer_stats
        customers_list = get_all_customers()
        stats = get_customer_stats() # Lấy số liệu thật
        return render_template('admin_customers.html', customers=customers_list, stats=stats)
    return redirect(url_for('login'))
@app.route('/edit_customer', methods=['POST'])
def edit_customer():
    if 'user_name' in session and session.get('role') == 'admin':
        success, message = edit_customer_action(request.form)
        flash(message, "success" if success else "error")
        return redirect(url_for('admin_customers'))
    return redirect(url_for('login'))

@app.route('/admin/delete_customer/<customer_id>')
def admin_delete_customer(customer_id): # Tên hàm phải khớp với url_for trong HTML
    if 'user_name' in session and session.get('role') == 'admin':
        success, message = delete_customer_action(customer_id)
        flash(message, "success" if success else "error")
        return redirect(url_for('admin_customers'))
    return redirect(url_for('login'))
# END CUSTOMER
#---------------------End Trang quar tri-----------



# ───── Trang chủ ─────
@app.route('/')
def home():
    # thêm user_name kiểm tra đăng nhập
    # Bước 1: Kiểm tra xem người dùng đã có tên trong phiên làm việc (session) chưa
    user_name = session.get('user_name')

    # Bước 2: Nếu CHƯA đăng nhập (biến user_name bị trống)
    if not user_name:
        # Lập tức chuyển hướng người dùng sang trang Đăng nhập
        return redirect(url_for('login'))
    # Dùng cache thay vì query DB mỗi lần vào trang chủ
    danh_sach_tinh = get_provinces_cached()

    # sửa lại: trả về username hiển thị lên giao diện
    return render_template('index.html', provinces=danh_sach_tinh, user_name=user_name)


# ───── Danh sách chuyến xe ─────
@app.route('/trip_list')
def trip_list():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Lấy tham số lọc từ URL
    diem_di  = unicodedata.normalize('NFC', request.args.get('diem_di', '').strip())
    diem_den = unicodedata.normalize('NFC', request.args.get('diem_den', '').strip())
    ngay_di  = request.args.get('ngay_di', '').strip()

    # 1. LẤY DANH SÁCH TỈNH TỪ CACHE (không query DB)
    clean_provinces = get_provinces_cached()

    # Chuyển ngày
    ngay_di_sql = None
    if ngay_di:
        try:
            from datetime import datetime
            ngay_di_sql = datetime.strptime(ngay_di, '%d/%m/%Y').strftime('%Y-%m-%d')
        except ValueError:
            ngay_di_sql = None

    # Sử dụng View vw_Trip_Details đã được tạo trong Database
    sql = """
        SELECT * FROM vw_Trip_Details
        WHERE 1=1
    """
    
    params = [] 

    # Chỉ giữ filter ngày trong SQL
    if ngay_di_sql:
        sql += " AND DATE(dep_time) = %s"
        params.append(ngay_di_sql)

    sql += " ORDER BY dep_time ASC"

    cursor.execute(sql, params)
    trips = cursor.fetchall()

    # 2. GỌT SẠCH DATA CHUYẾN XE VÀ XỬ LÝ GHẾ
    # Lọc bỏ chuyến xe bị thiếu thời gian (dep_time/arr_time NULL sẽ gây lỗi template)
    trips = [t for t in trips if t.get('dep_time') and t.get('arr_time')]

    for trip in trips:
        # Số ghế trống = Tổng ghế - Số ghế đã bị chiếm
        occupied = trip['occupied_seats_count'] if trip['occupied_seats_count'] else 0
        trip['free_seats'] = trip['capacity'] - occupied
        
        # Gọt sạch ký tự thừa ở tỉnh đi và tỉnh đến
        if trip['dep_province']: trip['dep_province'] = trip['dep_province'].strip()
        if trip['arr_province']: trip['arr_province'] = trip['arr_province'].strip()
        
        # Tách danh sách ghế ĐỎ
        trip['sold_seats'] = [s.strip() for s in trip['sold_seats_str'].split(',')] if trip['sold_seats_str'] else []
        
        # Tách danh sách ghế VÀNG
        trip['pending_seats'] = [s.strip() for s in trip['pending_seats_str'].split(',')] if trip['pending_seats_str'] else []

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
        provinces=clean_provinces,
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

    # Lấy thông tin từ request
    phone  = data.get('phone', '')
    name   = data.get('name', 'Khách vãng lai')
    email  = data.get('email', '')
    seats  = ','.join(data.get('seats', []))  # VD: 'A1,A2,B3'

    # Nếu đã đăng nhập thì truyền customer_id vào SP, ngược lại truyền chuỗi rỗng
    session_customer_id = session.get('user_id') or ''

    db = get_db_connection()
    # Dùng cursor thường để gọi CALL với OUT parameter
    cursor = db.cursor()
    try:
        # Gọi Stored Procedure sp_LockSeats
        # SP sẽ tự xử lý: tạo/tra cứu khách hàng, tạo Bill, Ticket, Ticket_Seat
        cursor.execute(
            "CALL sp_LockSeats(%s, %s, %s, %s, %s, %s, %s, @bill_id)",
            (
                session_customer_id,
                phone,
                name,
                email,
                data['trip_id'],
                data['total_price'],
                seats
            )
        )
        # Lấy giá trị OUT parameter @bill_id
        cursor.execute("SELECT @bill_id")
        row = cursor.fetchone()
        bill_id = row[0] if row else None
        db.commit()
        return jsonify({"success": True, "bill_id": bill_id})
    except mysql.connector.Error as err:
        db.rollback()
        return jsonify({"success": False, "error": err.msg})
    except Exception as e:
        db.rollback()
        return jsonify({"success": False, "error": str(e)})
    finally:
        cursor.close()
        db.close()

# ───── API Thông tin cá nhân ─────
@app.route('/api/thong_tin_ca_nhan', methods=['GET'])
def thong_tin_ca_nhan():
    customer_id = session.get('user_id')
    if not customer_id:
        return jsonify({"success": False, "error": "Chưa đăng nhập"})

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        # Gọi Procedure sp_LayThongTinCaNhan (xem truy_van_sql/sp_LayThongTinCaNhan.sql)
        cursor.execute("CALL sp_LayThongTinCaNhan(%s)", (customer_id,))
        info = cursor.fetchone()
        if not info:
            return jsonify({"success": False, "error": "Không tìm thấy thông tin tài khoản"})
        return jsonify({"success": True, "info": info})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    finally:
        cursor.close()
        db.close()

# ───── API Lấy lịch sử theo tài khoản ─────
@app.route('/api/lay_lich_su_tai_khoan', methods=['GET'])
def lay_lich_su_tai_khoan():
    customer_id = session.get('user_id')
    if not customer_id:
        return jsonify({"success": False, "error": "Chưa đăng nhập"})

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        # Gọi Procedure sp_LayLichSuTaiKhoan (xem truy_van_sql/sp_LayLichSuTaiKhoan.sql)
        cursor.execute("CALL sp_LayLichSuTaiKhoan(%s)", (customer_id,))
        history = cursor.fetchall()

        for item in history:
            if item['booking_date']:
                item['booking_date'] = item['booking_date'].strftime('%H:%M %d/%m/%Y')
            if item['dep_time']:
                item['dep_time'] = item['dep_time'].strftime('%H:%M %d/%m/%Y')
            if item['arr_time']:
                item['arr_time'] = item['arr_time'].strftime('%H:%M %d/%m/%Y')

        return jsonify({"success": True, "history": history})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    finally:
        cursor.close()
        db.close()


# ───── API Hủy vé theo tài khoản ─────
@app.route('/api/cancel_ticket_tai_khoan', methods=['POST'])
def cancel_ticket_tai_khoan():
    customer_id = session.get('user_id')
    if not customer_id:
        return jsonify({"success": False, "error": "Chưa đăng nhập."})

    data = request.get_json()
    bill_id = data.get('bill_id', '')

    if not bill_id:
        return jsonify({"success": False, "error": "Thiếu mã hóa đơn."})

    db = get_db_connection()
    cursor = db.cursor()
    try:
        # Gọi Procedure sp_HuyVeTaiKhoan — kiểm tra quyền sở hữu + điều kiện 24h
        cursor.execute("CALL sp_HuyVeTaiKhoan(%s, %s)", (customer_id, bill_id))
        db.commit()
        return jsonify({"success": True})
    except mysql.connector.Error as err:
        db.rollback()
        return jsonify({"success": False, "error": err.msg})
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
        # Gọi Stored Procedure sp_ConfirmPayment
        # SP tự kiểm tra hóa đơn tồn tại + đang chờ, rồi UPDATE status
        cursor.execute("CALL sp_ConfirmPayment(%s)", (data['bill_id'],))
        db.commit()
        return jsonify({"success": True})
    except mysql.connector.Error as err:
        db.rollback()
        return jsonify({"success": False, "error": err.msg})
    except Exception as e:
        db.rollback()
        return jsonify({"success": False, "error": str(e)})
    finally:
        cursor.close()
        db.close()

if __name__ == '__main__':
    app.run(debug=True)
