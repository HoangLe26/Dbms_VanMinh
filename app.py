from flask import Flask, render_template, request, session, redirect, url_for, flash
import mysql.connector
import unicodedata
from back_end.check_login import verify_account

app = Flask(__name__, static_folder='assets', static_url_path='/assets')
app.secret_key = 'vanminh_secret_key_2026'

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root", 
        password="2609", 
        database="dbms_vanminh"
    )

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
            # Lưu thẻ ra vào 
            session['user_name'] = user['name']
            session['user_id'] = user['customer_id']
            # Cấp phép thành công -> về Trang chủ
            return redirect(url_for('home'))
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
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT DISTINCT province FROM Location ORDER BY province")
    danh_sach_tinh = cursor.fetchall()
    cursor.close()
    db.close()

    # sửa lại: trả về username hiển thị lên giao diện
    return render_template('index.html', provinces=danh_sach_tinh ,user_name=user_name)


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

# ───── API Lấy lịch sử thiết bị (cũ - giữ lại để tương thích) ─────
@app.route('/api/lay_lich_su', methods=['POST'])
def lay_lich_su():
    data = request.get_json()
    device_bills = data.get('device_bills', '')
    
    if not device_bills.strip():
        return jsonify({"success": True, "history": []})
        
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("CALL sp_LayLichSuThietBi(%s)", (device_bills,))
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

# ───── API Hủy vé thiết bị ─────
@app.route('/api/cancel_ticket', methods=['POST'])
def cancel_ticket():
    data = request.get_json()
    bill_id = data.get('bill_id', '')
    
    if not bill_id:
        return jsonify({"success": False, "error": "Thiếu mã hóa đơn."})
        
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute("CALL sp_HuyVeThietBi(%s)", (bill_id,))
        db.commit()
        return jsonify({"success": True})
    except mysql.connector.Error as err:
        db.rollback()
        # err.msg chứa thông báo từ SIGNAL SQLSTATE '45000'
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
