DELIMITER $$

DROP PROCEDURE IF EXISTS sp_LockSeats $$

-- ===========================================================
-- sp_LockSeats: Đặt/giữ ghế — tạo Bill, Ticket, Ticket_Seat
-- ===========================================================
-- Tham số IN:
--   p_session_customer_id : customer_id từ session (NULL nếu chưa đăng nhập)
CREATE PROCEDURE sp_LockSeats(
    IN  p_session_customer_id VARCHAR(50),
    IN  p_phone               VARCHAR(20),
    IN  p_name                VARCHAR(100),
    IN  p_email               VARCHAR(100),
    IN  p_trip_id             VARCHAR(50),
    IN  p_total_price         DECIMAL(12, 2),
    IN  p_seats               TEXT,
    OUT p_bill_id             VARCHAR(50)
)
BEGIN
    -- ── Biến nội bộ 
    DECLARE v_customer_id   VARCHAR(50);
    DECLARE v_bill_id       VARCHAR(50);
    DECLARE v_tic_id        VARCHAR(50);
    DECLARE v_seat_id       VARCHAR(50);
    DECLARE v_seat_code     VARCHAR(50);
    DECLARE v_unit_price    DECIMAL(12, 2);
    DECLARE v_seat_count    INT DEFAULT 0;
    DECLARE v_remaining     TEXT;
    DECLARE v_idx           INT DEFAULT 0;

    -- Tự động ROLLBACK và ném lại lỗi cho tầng ứng dụng
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    -- ── BƯỚC 1: Xác định customer_id
    IF p_session_customer_id IS NOT NULL AND p_session_customer_id != '' THEN
        -- Người dùng đã đăng nhập → dùng luôn
        SET v_customer_id = p_session_customer_id;
    ELSE
        -- Khách vãng lai → tra theo số điện thoại
        SELECT customer_id
        INTO   v_customer_id
        FROM   Customer
        WHERE  phonenum = p_phone
        LIMIT  1;

        IF v_customer_id IS NULL THEN
            -- Chưa có trong DB → tạo mới
            SET v_customer_id = CONCAT('CUS_', UNIX_TIMESTAMP());
            INSERT INTO Customer (customer_id, name, phonenum, email, customer_type)
            VALUES (v_customer_id, p_name, p_phone, NULLIF(p_email, ''), 'normal');
        END IF;
    END IF;

    -- ── BƯỚC 2: Đếm số ghế để tính đơn giá mỗi vé 
    -- Số ghế = số dấu phẩy + 1  (VD: 'A1,A2,B3' → 3 ghế)
    SET v_seat_count  = 1 + (LENGTH(p_seats) - LENGTH(REPLACE(p_seats, ',', '')));
    SET v_unit_price  = p_total_price / v_seat_count;

    -- ── BƯỚC 3: Tạo mã hóa đơn duy nhất 
    SET v_bill_id = CONCAT('BILL_', UNIX_TIMESTAMP());

    -- ── BƯỚC 4: Bắt đầu transaction 
    START TRANSACTION;

        -- Chèn hóa đơn với trạng thái 'Đang chờ'
        INSERT INTO Bill (bill_id, total, method, status, date, customer_id)
        VALUES (v_bill_id, p_total_price, 'QR', 'Đang chờ', NOW(), v_customer_id);

        -- ── BƯỚC 5: Vòng lặp tách chuỗi ghế và chèn vé 
        SET v_remaining = p_seats;
        SET v_idx       = 0;

        WHILE v_remaining != '' DO
            -- Lấy mã ghế đầu tiên trong chuỗi còn lại
            IF LOCATE(',', v_remaining) > 0 THEN
                SET v_seat_code = TRIM(SUBSTRING_INDEX(v_remaining, ',', 1));
                SET v_remaining = TRIM(SUBSTRING(v_remaining, LOCATE(',', v_remaining) + 1));
            ELSE
                -- Đây là phần tử cuối cùng
                SET v_seat_code = TRIM(v_remaining);
                SET v_remaining = '';
            END IF;

            -- Tạo tic_id duy nhất: BILL_ + timestamp + index
            SET v_tic_id = CONCAT('TIC_', UNIX_TIMESTAMP(), v_idx);
            SET v_idx    = v_idx + 1;

            -- Lấy seat_id từ mã ghế (seat_code)
            SELECT seat_id
            INTO   v_seat_id
            FROM   Seat
            WHERE  TRIM(seat_code) = v_seat_code
            LIMIT  1;

            IF v_seat_id IS NULL THEN
                SIGNAL SQLSTATE '45000'
                    SET MESSAGE_TEXT = 'Lỗi: Không tìm thấy ghế trong hệ thống!';
            END IF;

            -- Chèn Ticket
            INSERT INTO Ticket (tic_id, price, trip_id, bill_id)
            VALUES (v_tic_id, v_unit_price, p_trip_id, v_bill_id);

            -- Chèn Ticket_Seat
            INSERT INTO Ticket_Seat (tic_id, seat_id)
            VALUES (v_tic_id, v_seat_id);

        END WHILE;

    COMMIT;

    -- ── BƯỚC 6: Trả về bill_id cho backend 
    SET p_bill_id = v_bill_id;

END$$

DELIMITER;