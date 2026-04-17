USE  dbms_vanminh;

-- =========================================================
-- NHÓM 1: CÁC BẢNG ĐỘC LẬP (KHÔNG CÓ KHÓA NGOẠI)
-- =========================================================

-- 1. Import Bến xe
LOAD DATA INFILE 'C:/ptit_dbms_data/locations.csv'
INTO TABLE Location
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

-- 2. Import Xe khách
LOAD DATA INFILE 'C:/ptit_dbms_data/buses.csv'
INTO TABLE Bus
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

-- 3. Import Khách hàng
LOAD DATA INFILE 'C:/ptit_dbms_data/customers.csv'
INTO TABLE Customer
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

-- 4. Import Sơ đồ Ghế mẫu
LOAD DATA INFILE 'C:/ptit_dbms_data/seats.csv'
INTO TABLE Seat
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;


-- =========================================================
-- NHÓM 2: CÁC BẢNG PHỤ THUỘC 
-- =========================================================

-- 5. Import Hóa đơn (Phụ thuộc Customer)
LOAD DATA INFILE 'C:/ptit_dbms_data/bills.csv'
INTO TABLE Bill
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS;

-- 6. Import Chuyến xe (Phụ thuộc Bus, Location)
LOAD DATA INFILE 'C:/ptit_dbms_data/trips.csv'
INTO TABLE Trip
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS;

-- 7. Import Vé (Phụ thuộc Bill, Trip)
LOAD DATA INFILE 'C:/ptit_dbms_data/tickets.csv'
INTO TABLE Ticket
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS;

-- 8. Import Chi tiết Vé - Ghế (Phụ thuộc Ticket, Seat)
LOAD DATA INFILE 'C:/ptit_dbms_data/ticket_seats.csv'
INTO TABLE Ticket_Seat
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS;