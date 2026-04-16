import csv
import random

# Số lượng xe bạn muốn tạo
so_luong_xe = 50

# Đầu biển số của các tỉnh phố phổ biến
ma_tinh = ['29B', '30F', '37B', '38B', '73B', '43B']

# 2 loại xe theo yêu cầu
loai_xe = [
    {'desc': 'Xe giường nằm 38 chỗ (Normal)', 'capacity': 38},
    {'desc': 'Xe Limousine 21 chỗ (VIP)', 'capacity': 21}
]

# Tạo và ghi dữ liệu ra file CSV
with open('buses.csv', mode='w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    
    # Ghi dòng tiêu đề (Header)
    writer.writerow(['license_plate', 'bus_description', 'capacity'])
    
    for _ in range(so_luong_xe):
        # Tạo biển số xe ngẫu nhiên (Ví dụ: 29B-123.45)
        tinh = random.choice(ma_tinh)
        so_dau = str(random.randint(100, 999))
        so_cuoi = str(random.randint(10, 99))
        license_plate = f"{tinh}-{so_dau}.{so_cuoi}"
        
        # Chọn ngẫu nhiên loại xe (Tỉ lệ 70% Normal, 30% VIP)
        xe = random.choices(loai_xe, weights=[70, 30], k=1)[0]
        
        # Ghi một dòng dữ liệu vào CSV
        writer.writerow([license_plate, xe['desc'], xe['capacity']])

print(f"✅ Đã tạo thành công file buses.csv với {so_luong_xe} chiếc xe khách!")