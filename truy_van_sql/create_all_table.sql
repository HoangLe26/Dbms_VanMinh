USE dbms_vanminh;
DROP TABLE IF EXISTS Ticket_Seat;
DROP TABLE IF EXISTS Ticket;
DROP TABLE IF EXISTS Trip;
DROP TABLE IF EXISTS Bill;
DROP TABLE IF EXISTS Seat;
DROP TABLE IF EXISTS Customer;
DROP TABLE IF EXISTS Bus;
DROP TABLE IF EXISTS Location;
-- =======================================================
-- 1. TẠO CÁC BẢNG ĐỘC LẬP (Không chứa khóa ngoại)
-- =======================================================
CREATE TABLE Location (
    loc_id VARCHAR(50) PRIMARY KEY,
    station VARCHAR(255) NOT NULL,
    province VARCHAR(100) NOT NULL
);

CREATE TABLE Bus (
    license_plate VARCHAR(50) PRIMARY KEY,
    bus_description VARCHAR(255),
    capacity INT
);

CREATE TABLE Customer (
    customer_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    customer_type ENUM('normal', 'special'), -- Khai báo ENUM trực tiếp trong MySQL
    phonenum VARCHAR(20),
    email VARCHAR(100),
    username VARCHAR(50) UNIQUE,
    password VARCHAR(255)
);

-- =======================================================
-- 2. TẠO CÁC BẢNG PHỤ THUỘC BẬC 1
-- =======================================================

-- Bảng Ghế (Thuộc về một chiếc Xe cụ thể)
CREATE TABLE Seat (
    seat_id VARCHAR(50) PRIMARY KEY,
    seat_code VARCHAR(50) -- VD: 'A1', 'B2', ...
);
-- Bảng Hóa Đơn (Do Khách hàng thanh toán & Thuộc về Tổ chức xe)
CREATE TABLE Bill (
    bill_id VARCHAR(50) PRIMARY KEY,
    discount DECIMAL(12, 2) DEFAULT 0,
    total DECIMAL(12, 2) NOT NULL,
    method ENUM('QR', 'Card', 'Cash'), -- Khai báo ENUM trực tiếp
    date DATETIME DEFAULT CURRENT_TIMESTAMP, -- Tự động lấy giờ hiện tại khi tạo Bill
    status VARCHAR(50), -- VD: 'Đã thanh toán', 'Hủy'
    customer_id VARCHAR(50),
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
);

-- Bảng Chuyến Xe (Có điểm đi/đến từ Location & Được chạy bởi Bus)
CREATE TABLE Trip (
    trip_id VARCHAR(50) PRIMARY KEY,
    dep_time DATETIME,
    arr_time DATETIME,
    duration INT, -- Tính bằng phút
    type ENUM('normal', 'vip'), -- Khai báo ENUM trực tiếp
    price DECIMAL(12, 2),
    dep_sta_id VARCHAR(50),
    arr_sta_id VARCHAR(50),
    license_plate VARCHAR(50),
    FOREIGN KEY (dep_sta_id) REFERENCES Location(loc_id),
    FOREIGN KEY (arr_sta_id) REFERENCES Location(loc_id),
    FOREIGN KEY (license_plate) REFERENCES Bus(license_plate)
);

-- =======================================================
-- 3. TẠO BẢNG PHỤ THUỘC BẬC 2 (Vé)
-- =======================================================

-- Bảng Vé (Nằm trong 1 Hóa đơn & Thuộc về 1 Chuyến xe)
CREATE TABLE Ticket (
    tic_id VARCHAR(50) PRIMARY KEY,
    price DECIMAL(12, 2) NOT NULL,
    bill_id VARCHAR(50),
    trip_id VARCHAR(50),
    FOREIGN KEY (bill_id) REFERENCES Bill(bill_id),
    FOREIGN KEY (trip_id) REFERENCES Trip(trip_id)
);

-- =======================================================
-- 4. TẠO BẢNG TRUNG GIAN (Xử lý quan hệ N-N giữa Vé và Ghế)
-- =======================================================

-- Bảng Ticket_Seat (Trong ERD của bạn là bảng "Has")
CREATE TABLE Ticket_Seat (
    tic_id VARCHAR(50),
    seat_id VARCHAR(50),
    PRIMARY KEY (tic_id, seat_id), -- Khóa chính kép
    FOREIGN KEY (tic_id) REFERENCES Ticket(tic_id),
    FOREIGN KEY (seat_id) REFERENCES Seat(seat_id)
);