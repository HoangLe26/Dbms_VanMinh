import csv

# Danh sách các bến xe phân theo tỉnh thành
locations_data = [
    # Hà Nội
    ('LOC_HN_001', 'Bến xe Nước Ngầm', 'Hà Nội'),
    ('LOC_HN_002', 'Bến xe Mỹ Đình', 'Hà Nội'),
    ('LOC_HN_003', 'Bến xe Giáp Bát', 'Hà Nội'),
    ('LOC_HN_004', 'Bến xe Yên Nghĩa', 'Hà Nội'),
    
    # Nghệ An
    ('LOC_NA_001', 'Bến xe Bắc Vinh', 'Nghệ An'),
    ('LOC_NA_002', 'Bến xe Chợ Vinh', 'Nghệ An'),
    ('LOC_NA_003', 'Bến xe Miền Trung', 'Nghệ An'),
    
    # Hà Tĩnh
    ('LOC_HT_001', 'Bến xe Hà Tĩnh', 'Hà Tĩnh'),
    ('LOC_HT_002', 'Bến xe Hồng Lĩnh', 'Hà Tĩnh'),
    ('LOC_HT_003', 'Bến xe Kỳ Anh', 'Hà Tĩnh'),
    
    # Quảng Bình
    ('LOC_QB_001', 'Bến xe Đồng Hới', 'Quảng Bình'),
    ('LOC_QB_002', 'Bến xe Ba Đồn', 'Quảng Bình'),
    ('LOC_QB_003', 'Bến xe Hoàn Lão', 'Quảng Bình'),
    
    # Đà Nẵng
    ('LOC_DN_001', 'Bến xe Trung tâm Đà Nẵng', 'Đà Nẵng'),
    ('LOC_DN_002', 'Bến xe Đức Long', 'Đà Nẵng')
]

# Tạo và ghi dữ liệu ra file CSV
with open('locations.csv', mode='w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    
    # Ghi dòng tiêu đề (Header)
    writer.writerow(['loc_id', 'station', 'province'])
    
    # Ghi từng dòng dữ liệu bến xe
    for loc in locations_data:
        writer.writerow(loc)

print(f"✅ Đã tạo thành công file locations.csv với {len(locations_data)} địa điểm!")