import csv
import random

# 1. Dựa theo sơ đồ xe giường nằm thực tế và xe Limousine ở Việt Nam
# Tầng 1: B, D, F
# Tầng 2: A, C, E
# Độ dài dãy: Tối đa 7 hàng (để hỗ trợ các dòng xe lên tới 40 chỗ)
tang_1 = [f"{day}{so}" for day in ['B', 'D', 'F'] for so in range(1, 8)] # B1-B7, D1-D7, F1-F7
tang_2 = [f"{day}{so}" for day in ['A', 'C', 'E'] for so in range(1, 8)] # A1-A7, C1-C7, E1-E7

# Gộp chung thành danh sách toàn bộ mã ghế (Tổng cộng 42 ghế để bao phủ mọi sơ đồ)
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