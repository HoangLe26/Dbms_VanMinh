DELIMITER $$

CREATE PROCEDURE sp_HuyVeThietBi(
    IN p_bill_id VARCHAR(50)
)
BEGIN
    DECLARE v_dep_time DATETIME;
    DECLARE v_status VARCHAR(50);
    DECLARE v_hours_diff INT;

    -- Xử lý lỗi an toàn
    DECLARE exit handler FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    -- Lấy thông tin Giờ xe chạy và Trạng thái hiện tại
    SELECT t.dep_time, b.status 
    INTO v_dep_time, v_status
    FROM Bill b
    JOIN Ticket tk ON b.bill_id = tk.bill_id
    JOIN Trip t ON tk.trip_id = t.trip_id
    WHERE b.bill_id = p_bill_id
    LIMIT 1;

    -- [KIỂM TRA 1]: Tồn tại
    IF v_dep_time IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Lỗi: Không tìm thấy hóa đơn này!';
    END IF;

    -- [KIỂM TRA 2]: Đã hủy chưa?
    IF v_status = 'Hủy' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Hóa đơn này đã được hủy trước đó.';
    END IF;

    -- [KIỂM TRA 3]: Xử lý Logic thời gian > 24h
    -- TIMESTAMPDIFF tính sự chênh lệch giờ giữa thời điểm hiện tại và giờ khởi hành
    SET v_hours_diff = TIMESTAMPDIFF(HOUR, NOW(), v_dep_time);

    IF v_hours_diff < 24 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Rất tiếc, theo quy định bạn chỉ có thể hủy/trả vé trước giờ xe chạy ít nhất 24 tiếng.';
    END IF;

    -- NẾU THỎA MÃN MỌI ĐIỀU KIỆN - TIẾN HÀNH HỦY!
    START TRANSACTION;

    -- 1. Cập nhật Bill sang Hủy (Để kế toán vẫn thấy được biên lai báo hủy)
    UPDATE Bill 
    SET status = 'Hủy' 
    WHERE bill_id = p_bill_id;

    -- 2. GIẢI PHÓNG GHẾ: Xóa mạnh tay vào Ticket_Seat để vé đó trở thành ghế trống vĩnh viễn
    -- Dùng câu lệnh DELETE kèm JOIN trong MySQL
    DELETE ts FROM Ticket_Seat ts
    INNER JOIN Ticket tk ON ts.tic_id = tk.tic_id
    WHERE tk.bill_id = p_bill_id;

    COMMIT;
    
    -- Option: Có thể nhét thêm vào bảng Lich_Su_Huy (nếu bạn có)

END$$

DELIMITER ;
