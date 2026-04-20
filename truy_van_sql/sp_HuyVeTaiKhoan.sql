DELIMITER $$

DROP PROCEDURE IF EXISTS sp_HuyVeTaiKhoan $$

CREATE PROCEDURE sp_HuyVeTaiKhoan(
    IN p_customer_id VARCHAR(50),
    IN p_bill_id     VARCHAR(50)
)
BEGIN
    DECLARE v_dep_time   DATETIME;
    DECLARE v_status     VARCHAR(50);
    DECLARE v_owner_id   VARCHAR(50);
    DECLARE v_hours_diff INT;

    -- Xử lý lỗi an toàn: tự động ROLLBACK và ném lại lỗi cho tầng ứng dụng
    DECLARE exit handler FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    -- Lấy thông tin giờ xe chạy, trạng thái và chủ sở hữu hóa đơn
    SELECT t.dep_time, b.status, b.customer_id
    INTO   v_dep_time, v_status, v_owner_id
    FROM   Bill b
    JOIN   Ticket tk ON tk.bill_id  = b.bill_id
    JOIN   Trip   t  ON t.trip_id   = tk.trip_id
    WHERE  b.bill_id = p_bill_id
    LIMIT 1;

    -- [KIỂM TRA 1]: Hóa đơn có tồn tại không?
    IF v_dep_time IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Lỗi: Không tìm thấy hóa đơn này!';
    END IF;

    -- [KIỂM TRA 2]: Hóa đơn có thuộc về tài khoản đang đăng nhập không?
    IF v_owner_id != p_customer_id THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Lỗi: Bạn không có quyền hủy hóa đơn này!';
    END IF;

    -- [KIỂM TRA 3]: Hóa đơn đã bị hủy trước đó chưa?
    IF v_status = 'Hủy' THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Hóa đơn này đã được hủy trước đó.';
    END IF;

    -- [KIỂM TRA 4]: Còn đủ ít nhất 24 tiếng trước giờ xe chạy?
    SET v_hours_diff = TIMESTAMPDIFF(HOUR, NOW(), v_dep_time);

    IF v_hours_diff < 24 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Rất tiếc, theo quy định bạn chỉ có thể hủy/trả vé trước giờ xe chạy ít nhất 24 tiếng.';
    END IF;

    -- NẾU THỎA MÃN MỌI ĐIỀU KIỆN => TIẾN HÀNH HỦY!
    START TRANSACTION;

        -- 1. Đánh dấu hóa đơn là 'Hủy' (giữ lại để kế toán vẫn thấy biên lai)
        UPDATE Bill
        SET    status = 'Hủy'
        WHERE  bill_id = p_bill_id;

        -- 2. Giải phóng ghế: xóa các dòng Ticket_Seat để ghế trở thành trống
        DELETE ts
        FROM   Ticket_Seat ts
        INNER JOIN Ticket tk ON ts.tic_id = tk.tic_id
        WHERE  tk.bill_id = p_bill_id;

    COMMIT;

END$$

DELIMITER ;
