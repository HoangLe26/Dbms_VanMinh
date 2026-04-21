DELIMITER $$

DROP PROCEDURE IF EXISTS sp_ConfirmPayment $$

-- ===========================================================
-- sp_ConfirmPayment: Xác nhận thanh toán hóa đơn
-- ===========================================================
-- Tham số IN:
--   p_bill_id : Mã hóa đơn cần xác nhận
-- ===========================================================
CREATE PROCEDURE sp_ConfirmPayment(
    IN p_bill_id VARCHAR(50)
)
BEGIN
    DECLARE v_status VARCHAR(50);

    -- Tự động ROLLBACK và ném lại lỗi cho tầng ứng dụng
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    -- ── BƯỚC 1: Kiểm tra hóa đơn có tồn tại không ────────────
    SELECT status
    INTO   v_status
    FROM   Bill
    WHERE  bill_id = p_bill_id
    LIMIT  1;

    IF v_status IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Lỗi: Không tìm thấy hóa đơn này!';
    END IF;

    -- ── BƯỚC 2: Kiểm tra hóa đơn có đang ở trạng thái chờ không
    IF v_status != 'Đang chờ' THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Lỗi: Hóa đơn này không ở trạng thái chờ thanh toán!';
    END IF;

    -- ── BƯỚC 3: Cập nhật trạng thái → 'Đã thanh toán' ────────
    START TRANSACTION;

        UPDATE Bill
        SET    status = 'Đã thanh toán'
        WHERE  bill_id = p_bill_id;

    COMMIT;

END$$

DELIMITER ;
