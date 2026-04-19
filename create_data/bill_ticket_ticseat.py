import csv
import random
from datetime import timedelta

# ==========================================
# 1. Đọc dữ liệu nền tảng
# ==========================================
customers = []
with open('create_data/customers.csv', mode='r', encoding='utf-8') as f:
    customers = [row['customer_id'] for row in csv.DictReader(f)]

trips = {}
with open('create_data/trips.csv', mode='r', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        trips[row['trip_id']] = {
            'price': float(row['price']),
            'license_plate': row['license_plate'],
            'dep_time': row['dep_time']
        }

# LẤY DANH SÁCH TOÀN BỘ GHẾ MẪU
# (Vì bảng Seat giờ là template nên mọi chuyến xe đều dùng chung bộ ghế này)
all_template_seats = []
with open('create_data/seats.csv', mode='r', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        all_template_seats.append(row['seat_id'])

# ==========================================
# 2. Xử lý logic Đặt vé (Booking)
# ==========================================
so_luong_hoa_don = 150 # Tạo 150 lượt mua vé
bills_data = []
tickets_data = []
ticket_seats_data = []

# Sổ xé nháp nhớ xem ghế nào đã bị đặt trong chuyến nào { 'TRIP_001': ['SEAT_001', 'SEAT_002'] }
booked_seats_tracker = {} 

ticket_counter = 1

for i in range(1, so_luong_hoa_don + 1):
    bill_id = f"BILL_{i:04d}"
    cus_id = random.choice(customers)
    trip_id = random.choice(list(trips.keys()))
    
    trip_info = trips[trip_id]
    gia_ve = trip_info['price']
    
    # Số lượng vé khách muốn mua (1 đến 3 vé)
    so_luong_ve = random.randint(1, 3)
    
    # Tìm những ghế trống của chuyến này
    booked_seats = booked_seats_tracker.get(trip_id, [])
    # Ghế trống = Toàn bộ ghế mẫu trừ đi những ghế đã có người mua trong chuyến này
    available_seats = [s for s in all_template_seats if s not in booked_seats]
    
    if len(available_seats) < so_luong_ve:
        continue # Nếu không đủ ghế thì bỏ qua hóa đơn này, sang phục vụ người khác
        
    # Bốc ghế ngẫu nhiên cho khách
    chosen_seats = random.sample(available_seats, so_luong_ve)
    
    # Ghi chú lại vào sổ để người sau không mua trùng
    if trip_id not in booked_seats_tracker:
        booked_seats_tracker[trip_id] = []
    booked_seats_tracker[trip_id].extend(chosen_seats)
    
    # --- TẠO DATA HÓA ĐƠN ---
    discount = 0
    total = so_luong_ve * gia_ve
    method = random.choice(['QR', 'Card', 'Cash'])
    status = 'Đã thanh toán'
    bill_date = "2026-04-18 10:30:00" # Giả lập 1 mốc thời gian mua
    

    if random.random() < 0.8:
        status = 'Đã thanh toán'
        bill_date = "2026-04-18 10:30:00" 
    else:
        status = 'Đang chờ'
        # Quan trọng: Lấy giờ hiện tại để logic 60s trong SQL có tác dụng
        bill_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
    bills_data.append([bill_id, discount, total, method, bill_date, status, cus_id])

# Giả sử bạn muốn tạo 40 bill test trạng thái khác nhau
for i in range(40):
    # ... logic tạo ID ...
    
    # Chia tỉ lệ: 80% đã thanh toán, 20% đang chờ để test màu vàng
    if random.random() < 0.8:
        status = 'Đã thanh toán'
        bill_date = "2026-04-18 10:30:00" 
    else:
        status = 'Đang chờ'
        # Quan trọng: Lấy giờ hiện tại để logic 60s trong SQL có tác dụng
        bill_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    bills_data.append([bill_id, discount, total, method, bill_date, status, cus_id])



    # --- TẠO DATA VÉ & CHI TIẾT VÉ-GHẾ ---
    for seat_id in chosen_seats:
        tic_id = f"TIC_{ticket_counter:05d}"
        
        # Bảng Ticket
        tickets_data.append([tic_id, gia_ve, bill_id, trip_id])
        
        # Bảng Ticket_Seat
        ticket_seats_data.append([tic_id, seat_id])
        
        ticket_counter += 1

# ==========================================
# 3. Xuất ra 3 file CSV
# ==========================================
with open('create_data/bills.csv', mode='w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['bill_id', 'discount', 'total', 'method', 'date', 'status', 'customer_id'])
    writer.writerows(bills_data)

with open('create_data/tickets.csv', mode='w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['tic_id', 'price', 'bill_id', 'trip_id'])
    writer.writerows(tickets_data)

with open('create_data/ticket_seats.csv', mode='w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['tic_id', 'seat_id'])
    writer.writerows(ticket_seats_data)

print(f"✅ Đã tạo THÀNH CÔNG 3 file: bills.csv, tickets.csv, ticket_seats.csv!")
print(f"🎉 Khách đã mua tổng cộng {ticket_counter - 1} vé. Chúc mừng hệ thống của bạn đã hoàn thiện 100%!")