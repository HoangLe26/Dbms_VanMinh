USE dbms_vanminh;
-- Đổi ký tự kết thúc lệnh thành $$
DELIMITER $$
CREATE TRIGGER trg_Prevent_Late_Booking
BEFORE INSERT ON Ticket
FOR EACH ROW
BEGIN
    DECLARE trip_departure DATETIME;

    -- Bước 1: Xem giờ khởi hành
    SELECT dep_time INTO trip_departure
    FROM Trip
    WHERE trip_id = NEW.trip_id;

    -- Bước 2: Bắt chuyến xe đã chạy
    IF NOW() > trip_departure THEN
        -- Bước 3: Block lệnh INSERT
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Lỗi: Chuyến xe này đã khởi hành, không thể đặt thêm vé!';
    END IF;
END$$ -- Kết thúc trigger bằng $$

-- Trả lại ký tự kết thúc lệnh mặc định là ;
DELIMITER ;