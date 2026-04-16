import csv
import random

# 1. Dựa theo sơ đồ xe giường nằm thực tế ở Việt Nam (như ảnh bạn gửi)
# Tầng 1 thường là các dãy B, D, F, M...
# Tầng 2 thường là các dãy A, C, E, S...
# Ở đây tôi tạo một sơ đồ mẫu khoảng 38 - 40 chỗ.
tang_1 = [f"{day}{so}" for day in ['B', 'D', 'F'] for so in range(1, 7)] # B1-B6, D1-D6, F1-F6
tang_2 = [f"{day}{so}" for day in ['A', 'C', 'E'] for so in range(1, 7)] # A1-A6, C1-C6, E1-E6

# Gộp chung thành danh sách toàn bộ mã ghế
danh_sach_ma_ghe = tang_1 + tang_2

# 2. Tạo và ghi dữ liệu ra file CSV
with open('seats.csv', mode='w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    
    # Ghi dòng tiêu đề (Header)
    writer.writerow(['seat_id', 'status', 'seat_code'])
    
    for i, code in enumerate(danh_sach_ma_ghe, start=1):
        # Tạo ID ghế (VD: SEAT_001, SEAT_002...)
        seat_id = f"SEAT_{i:03d}"
        
        
        # Ghi một dòng dữ liệu vào CSV
        writer.writerow([seat_id, code])

print(f"✅ Đã tạo thành công file seats.csv với {len(danh_sach_ma_ghe)} chiếc ghế mẫu!")