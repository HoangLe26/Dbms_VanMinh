import random
import unicodedata
import csv

# 1. Chuẩn bị tập dữ liệu để random ghép tên
ho_list = ['Nguyễn', 'Trần', 'Lê', 'Phạm', 'Hoàng', 'Huỳnh', 'Phan', 'Vũ', 'Võ', 'Đặng', 'Bùi', 'Đỗ', 'Hồ', 'Ngô', 'Dương']
dem_list = ['Văn', 'Thị', 'Ngọc', 'Minh', 'Xuân', 'Thu', 'Hữu', 'Đức', 'Hải', 'Thanh', 'Tuấn', 'Quang', 'Hồng', 'Gia', 'Bảo', 'Đình']
ten_list = ['An', 'Bình', 'Châu', 'Dương', 'Hải', 'Khang', 'Linh', 'Phong', 'Nghĩa', 'Phúc', 'Tâm', 'Anh', 'Khoa', 'Vy', 'Trang', 'Hùng', 'Duy', 'Huy', 'Nhung']

# Hàm loại bỏ dấu tiếng Việt để tạo username và email cho chuẩn xác
def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)]).replace('đ', 'd').replace('Đ', 'D')

# Số lượng khách hàng muốn tạo
so_luong = 200

# 2. Bắt đầu tạo file CSV
with open('customers.csv', mode='w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    
    # Ghi dòng tiêu đề (Header)
    writer.writerow(['customer_id', 'name', 'customer_type', 'phonenum', 'email', 'username', 'password'])
    
    for i in range(1, so_luong + 1):
        # ID: CUS_001, CUS_002...
        customer_id = f"CUS_{i:03d}"
        
        # Tên: Ghép Họ + Đệm + Tên
        ho = random.choice(ho_list)
        dem = random.choice(dem_list)
        ten = random.choice(ten_list)
        full_name = f"{ho} {dem} {ten}"
        
        # Loại KH: Random 80% là normal, 20% là special
        customer_type = random.choices(['normal', 'special'], weights=[80, 20], k=1)[0]
        
        # SDT: Bắt đầu bằng 09, 08, 03, 07 + 8 số ngẫu nhiên
        dau_so = random.choice(['09', '08', '03', '07'])
        phonenum = dau_so + ''.join([str(random.randint(0, 9)) for _ in range(8)])
        
        # Username & Email: Chuyển tên thành không dấu viết liền + ID để tránh trùng lặp 100%
        clean_ten = remove_accents(ten).lower()
        clean_ho = remove_accents(ho).lower()
        username = f"{clean_ten}{clean_ho}{i}"
        email = f"{username}@gmail.com"
        
        # Password: Để chung 1 chuỗi giả lập mật khẩu đã mã hóa
        password = "hashed_password_123!"
        
        # Ghi một dòng dữ liệu vào CSV
        writer.writerow([customer_id, full_name, customer_type, phonenum, email, username, password])

print(f"✅ Đã tạo thành công file customers.csv với {so_luong} dòng!")