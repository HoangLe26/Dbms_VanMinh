USE dbms_vanminh;

DELIMITER $$

DROP PROCEDURE IF EXISTS sp_CapNhatThongTin $$

-- ================================================================
-- sp_CapNhatThongTin: Cập nhật thông tin cá nhân khách hàng
-- ================================================================
-- Tham số IN:
--   p_customer_id : Mã khách hàng đang đăng nhập (lấy từ session)
--   p_new_name    : Họ tên mới (NULL = giữ nguyên)
--   p_new_phone   : Số điện thoại mới (NULL = giữ nguyên)
--   p_new_email   : Email mới (NULL = giữ nguyên)
-- ================================================================
CREATE PROCEDURE sp_CapNhatThongTin(
    IN p_customer_id VARCHAR(50),
    IN p_new_name    VARCHAR(100),
    IN p_new_phone   VARCHAR(20),
    IN p_new_email   VARCHAR(100)
)
BEGIN
    DECLARE v_existing_phone_owner VARCHAR(50);
    DECLARE v_existing_email_owner VARCHAR(50);
    DECLARE v_customer_exists      INT DEFAULT 0;

    -- Tự động ROLLBACK và ném lại lỗi nếu có SQLEXCEPTION xảy ra
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    -- ══════════════════════════════════════════════════════════════
    -- ĐIỂM ĐẦU: Bắt đầu Transaction
    -- ══════════════════════════════════════════════════════════════
    START TRANSACTION;

    -- ── OPERATION 1: Kiểm tra tài khoản cần cập nhật có tồn tại ──
    SELECT COUNT(*) INTO v_customer_exists
    FROM Customer
    WHERE customer_id = p_customer_id;

    IF v_customer_exists = 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Lỗi: Không tìm thấy tài khoản này trong hệ thống!';
    END IF;

    -- ── OPERATION 2: Kiểm tra số điện thoại mới có bị trùng không ──
    -- Chỉ kiểm tra nếu người dùng có yêu cầu đổi số điện thoại
    IF p_new_phone IS NOT NULL AND p_new_phone != '' THEN

        SELECT customer_id INTO v_existing_phone_owner
        FROM Customer
        WHERE phonenum = p_new_phone
          AND customer_id != p_customer_id   -- Loại trừ chính tài khoản đang sửa
        LIMIT 1;

        IF v_existing_phone_owner IS NOT NULL THEN
            SIGNAL SQLSTATE '45001'
                SET MESSAGE_TEXT = 'Lỗi: Số điện thoại này đã được đăng ký bởi tài khoản khác!';
        END IF;
    END IF;

    -- ── OPERATION 3: Kiểm tra email mới có bị trùng không ──
    -- Chỉ kiểm tra nếu người dùng có yêu cầu đổi email
    IF p_new_email IS NOT NULL AND p_new_email != '' THEN

        SELECT customer_id INTO v_existing_email_owner
        FROM Customer
        WHERE email = p_new_email
          AND customer_id != p_customer_id   -- Loại trừ chính tài khoản đang sửa
        LIMIT 1;

        IF v_existing_email_owner IS NOT NULL THEN
            SIGNAL SQLSTATE '45002'
                SET MESSAGE_TEXT = 'Lỗi: Email này đã được đăng ký bởi tài khoản khác!';
        END IF;
    END IF;

    -- ── OPERATION 4: Thực hiện cập nhật ──
    -- Dùng COALESCE để giữ nguyên giá trị cũ nếu tham số đầu vào là NULL/rỗng
    UPDATE Customer
    SET
        name    = CASE
                    WHEN p_new_name  IS NOT NULL AND p_new_name  != '' THEN p_new_name
                    ELSE name
                  END,
        phonenum = CASE
                    WHEN p_new_phone IS NOT NULL AND p_new_phone != '' THEN p_new_phone
                    ELSE phonenum
                  END,
        email   = CASE
                    WHEN p_new_email IS NOT NULL AND p_new_email != '' THEN p_new_email
                    WHEN p_new_email = ''                              THEN NULL  -- Cho phép xóa email
                    ELSE email
                  END
    WHERE customer_id = p_customer_id;

    -- ══════════════════════════════════════════════════════════════
    -- ĐIỂM CUỐI: Tất cả 4 Operations thành công → COMMIT
    -- ══════════════════════════════════════════════════════════════
    COMMIT;

    -- Trả về thông tin mới nhất sau khi cập nhật để Frontend cập nhật lại UI
    SELECT name, phonenum, email, customer_type
    FROM Customer
    WHERE customer_id = p_customer_id;

END$$

DELIMITER ;
