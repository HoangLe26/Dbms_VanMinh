-- =======================================================
-- TỐI ƯU HÓA: TẠO INDEX CHO CÁC CỘT THƯỜNG ĐƯỢC TRUY VẤN
-- =======================================================
-- Index giúp MySQL tìm kiếm nhanh hơn bằng cách tạo "mục lục"
-- thay vì quét toàn bộ bảng (Full Table Scan).
-- Chạy file này 1 lần duy nhất để áp dụng.
-- =======================================================

USE dbms_vanminh;

-- ─────────────────────────────────────────────────────────
-- BẢNG Bill: Hay được lọc theo customer_id và status
-- Dùng trong: sp_ConfirmPayment, sp_HuyVeTaiKhoan,
--             sp_LayLichSuTaiKhoan, vw_Trip_Details
-- ─────────────────────────────────────────────────────────
CREATE INDEX idx_bill_customer ON Bill (customer_id);

CREATE INDEX idx_bill_status ON Bill (status);

CREATE INDEX idx_bill_date ON Bill (date);

-- Index kết hợp: lọc theo status VÀ date cùng lúc (dùng trong vw_Trip_Details)
CREATE INDEX idx_bill_status_date ON Bill (status, date);

-- ─────────────────────────────────────────────────────────
-- BẢNG Ticket: Hay được JOIN với Bill và Trip
-- Dùng trong: vw_Trip_Details, sp_HuyVeTaiKhoan
-- ─────────────────────────────────────────────────────────
CREATE INDEX idx_ticket_bill ON Ticket (bill_id);

CREATE INDEX idx_ticket_trip ON Ticket (trip_id);

-- ─────────────────────────────────────────────────────────
-- BẢNG Ticket_Seat: Bảng trung gian, hay được JOIN
-- Dùng trong: vw_Trip_Details (đếm ghế đã bán, ghế đang giữ)
-- ─────────────────────────────────────────────────────────
CREATE INDEX idx_ticket_seat_tic ON Ticket_Seat (tic_id);

CREATE INDEX idx_ticket_seat_seat ON Ticket_Seat (seat_id);

-- ─────────────────────────────────────────────────────────
-- BẢNG Trip: Hay được lọc theo thời gian khởi hành
-- Dùng trong: trip_list (lọc ngày đi)
-- ─────────────────────────────────────────────────────────
CREATE INDEX idx_trip_dep_time ON Trip (dep_time);

-- ─────────────────────────────────────────────────────────
-- BẢNG Customer: Hay được tìm theo username và phonenum
-- Dùng trong: check_login, đăng ký tài khoản
-- ─────────────────────────────────────────────────────────
-- username đã có UNIQUE index (tự động từ schema), không cần thêm.
CREATE INDEX idx_customer_phone ON Customer (phonenum);

-- ─────────────────────────────────────────────────────────
-- KIỂM TRA: Xem các index đã tạo
-- ─────────────────────────────────────────────────────────
-- SHOW INDEX FROM Bill;
-- SHOW INDEX FROM Ticket;
-- SHOW INDEX FROM Ticket_Seat;
-- SHOW INDEX FROM Trip;
-- SHOW INDEX FROM Customer;