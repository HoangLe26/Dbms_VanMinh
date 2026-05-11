USE dbms_vanminh;

DELIMITER $$

DROP PROCEDURE IF EXISTS sp_NhuongVe $$

-- ================================================================
-- sp_NhuongVe: Nhượng toàn bộ hóa đơn cho người khác
-- ================================================================
-- Đây là một TRANSACTION CHUẨN với 2 lệnh GHI trên 2 bảng:
--   Op.1 (Có điều kiện): INSERT INTO Customer  → Tạo tài khoản người nhận
--   Op.2              :  UPDATE Bill            → Đổi chủ sở hữu hóa đơn
--
-- Nguyên tắc ATOMICITY:
--   - Nếu Op.1 thành công nhưng Op.2 FAIL → ROLLBACK xóa Customer vừa tạo
--   - Hóa đơn vẫn đứng tên người chuyển, không có tài khoản "mồ côi" nào tồn tại
--
-- Tham số IN:
--   p_owner_id       : customer_id của người ĐANG đăng nhập (chủ hóa đơn hiện tại)
--   p_bill_id        : Mã hóa đơn muốn nhượng
--   p_phone_nhan     : Số điện thoại của người NHẬN vé
--   p_ten_nhan       : Họ tên người nhận (dùng khi tạo tài khoản mới)
-- ================================================================
CREATE PROCEDURE sp_NhuongVe(
    IN p_owner_id   VARCHAR(50),
    IN p_bill_id    VARCHAR(50),
    IN p_phone_nhan VARCHAR(20),
    IN p_ten_nhan   VARCHAR(100)
)
BEGIN
    -- ── Biến kiểm tra ─────────────────────────────────────────────
    DECLARE v_bill_owner    VARCHAR(50);
    DECLARE v_bill_status   VARCHAR(50);
    DECLARE v_dep_time      DATETIME;
    DECLARE v_receiver_id   VARCHAR(50);
    DECLARE v_hours_to_dep  INT;

    -- ── Tự động ROLLBACK toàn bộ nếu có lỗi SQL bất kỳ ───────────
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    -- ══════════════════════════════════════════════════════════════
    -- KIỂM TRA ĐIỀU KIỆN (trước khi mở Transaction)
    -- ══════════════════════════════════════════════════════════════

    -- [CHECK 1] Hóa đơn có tồn tại và có thuộc người này không?
    SELECT b.customer_id, b.status, t.dep_time
    INTO   v_bill_owner, v_bill_status, v_dep_time
    FROM   Bill b
    JOIN   Ticket  tk ON tk.bill_id  = b.bill_id
    JOIN   Trip    t  ON t.trip_id   = tk.trip_id
    WHERE  b.bill_id = p_bill_id
    LIMIT  1;

    IF v_bill_owner IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Lỗi: Không tìm thấy hóa đơn này trong hệ thống!';
    END IF;

    IF v_bill_owner != p_owner_id THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Lỗi: Bạn không phải chủ sở hữu của hóa đơn này!';
    END IF;

    -- [CHECK 2] Hóa đơn phải ở trạng thái đã thanh toán mới được nhượng
    IF v_bill_status != 'Đã thanh toán' THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Lỗi: Chỉ có thể nhượng hóa đơn đã thanh toán thành công!';
    END IF;

    -- [CHECK 3] Chuyến xe chưa khởi hành (còn ít nhất 2 tiếng)
    SET v_hours_to_dep = TIMESTAMPDIFF(HOUR, NOW(), v_dep_time);
    IF v_hours_to_dep < 2 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Lỗi: Chỉ có thể nhượng vé khi còn ít nhất 2 tiếng trước giờ khởi hành!';
    END IF;

    -- [CHECK 4] Không được nhượng cho chính mình
    SELECT customer_id INTO v_receiver_id
    FROM   Customer
    WHERE  phonenum = p_phone_nhan
    LIMIT  1;

    IF v_receiver_id = p_owner_id THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Lỗi: Không thể nhượng vé cho chính tài khoản của bạn!';
    END IF;

    -- ══════════════════════════════════════════════════════════════
    -- ĐIỂM ĐẦU TRANSACTION
    -- ══════════════════════════════════════════════════════════════
    START TRANSACTION;

        -- ── OPERATION 1: Xử lý tài khoản người nhận ───────────────
        -- Nếu số điện thoại chưa có trong hệ thống → tạo mới
        IF v_receiver_id IS NULL THEN

            IF p_ten_nhan IS NULL OR TRIM(p_ten_nhan) = '' THEN
                SIGNAL SQLSTATE '45000'
                    SET MESSAGE_TEXT = 'Lỗi: Người nhận chưa có tài khoản, vui lòng cung cấp họ tên để tạo mới!';
            END IF;

            SET v_receiver_id = CONCAT('CUS_', UNIX_TIMESTAMP(), '_NV');

            -- GHI vào Bảng 1: Customer
            INSERT INTO Customer (customer_id, name, phonenum, customer_type)
            VALUES (v_receiver_id, TRIM(p_ten_nhan), p_phone_nhan, 'normal');

        END IF;

        -- ── OPERATION 2: Chuyển quyền sở hữu hóa đơn ─────────────
        -- GHI vào Bảng 2: Bill
        UPDATE Bill
        SET    customer_id = v_receiver_id
        WHERE  bill_id     = p_bill_id;

        -- Kiểm tra UPDATE có thực sự ảnh hưởng đến đúng 1 dòng không
        IF ROW_COUNT() = 0 THEN
            SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Lỗi: Không thể cập nhật hóa đơn, vui lòng thử lại!';
        END IF;

    -- ══════════════════════════════════════════════════════════════
    -- ĐIỂM CUỐI: Cả 2 Operations thành công → COMMIT
    -- ══════════════════════════════════════════════════════════════
    COMMIT;

    -- Trả về thông tin xác nhận cho Frontend
    SELECT
        p_bill_id                AS bill_id,
        v_receiver_id            AS new_owner_id,
        p_phone_nhan             AS receiver_phone,
        COALESCE(p_ten_nhan, (SELECT name FROM Customer WHERE customer_id = v_receiver_id)) AS receiver_name,
        'Nhượng vé thành công'   AS message;

END$$

DELIMITER ;
