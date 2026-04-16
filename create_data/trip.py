import csv
import random
from datetime import datetime, timedelta

# ==========================================
# 1. Đọc dữ liệu Bến xe (Lấy cả ID và Tỉnh)
# ==========================================
locations = []
try:
    with open('create_data/locations.csv', mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Lưu lại cả loc_id và province để check điều kiện khác tỉnh
            locations.append({'loc_id': row['loc_id'], 'province': row['province']})
except FileNotFoundError:
    print("❌ Không tìm thấy locations.csv. Hãy đảm bảo file ở cùng thư mục.")
    exit()

# ==========================================
# 2. Đọc dữ liệu Xe khách
# ==========================================
buses = []
try:
    with open('create_data/buses.csv', mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            bus_type = 'vip' if 'VIP' in row['bus_description'] else 'normal'
            buses.append({'plate': row['license_plate'], 'type': bus_type})
except FileNotFoundError:
    print("❌ Không tìm thấy buses.csv. Hãy đảm bảo file ở cùng thư mục.")
    exit()

# ==========================================
# 3. Tạo dữ liệu Chuyến xe (Từ 20/04 - 25/04)
# ==========================================
so_luong_chuyen = 100
trips_data = []

# Đặt mốc thời gian từ 20/04/2026 đến 25/04/2026
start_date = datetime(2026, 4, 20)
end_date = datetime(2026, 4, 25)
days_range = (end_date - start_date).days # Tính ra chênh lệch là 5 ngày

for i in range(1, so_luong_chuyen + 1):
    trip_id = f"TRIP_{i:04d}"
    
    # 3.1. Chọn ngẫu nhiên 1 xe
    xe_chay = random.choice(buses)
    license_plate = xe_chay['plate']
    trip_type = xe_chay['type']
    
    # 3.2. Chọn điểm đi và đến: ĐẢM BẢO KHÁC TỈNH
    while True:
        # Bốc ngẫu nhiên 2 bến xe
        dep_sta, arr_sta = random.sample(locations, 2)
        
        # Nếu tỉnh của bến đi KHÁC tỉnh của bến đến thì mới thoát vòng lặp
        if dep_sta['province'] != arr_sta['province']:
            break
            
    dep_sta_id = dep_sta['loc_id']
    arr_sta_id = arr_sta['loc_id']
    
    # 3.3. Tính giá vé
    price = random.choice([350000, 400000]) if trip_type == 'vip' else random.choice([200000, 250000])
    
    # 3.4. Random ngày khởi hành từ 20 -> 25/4
    random_days = random.randint(0, days_range)
    ngay_khoi_hanh = start_date + timedelta(days=random_days)
    
    # Random giờ khởi hành (5h sáng -> 22h đêm)
    gio_khoi_hanh = random.randint(5, 22) 
    dep_time = ngay_khoi_hanh.replace(hour=gio_khoi_hanh, minute=0, second=0, microsecond=0)
    
    # Random thời gian chạy và tính giờ đến
    duration = random.randint(240, 480) # từ 4 -> 8 tiếng
    arr_time = dep_time + timedelta(minutes=duration)
    
    dep_time_str = dep_time.strftime('%Y-%m-%d %H:%M:%S')
    arr_time_str = arr_time.strftime('%Y-%m-%d %H:%M:%S')
    
    trips_data.append([trip_id, dep_time_str, arr_time_str, duration, trip_type, price, dep_sta_id, arr_sta_id, license_plate])

# ==========================================
# 4. Ghi ra file trips.csv
# ==========================================
with open('trips.csv', mode='w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['trip_id', 'dep_time', 'arr_time', 'duration', 'type', 'price', 'dep_sta_id', 'arr_sta_id', 'license_plate'])
    writer.writerows(trips_data)

print(f"✅ Đã tạo thành công file trips.csv với {so_luong_chuyen} chuyến xe (Đảm bảo chỉ trong 20-25/04 và 100% không trùng tỉnh)!")