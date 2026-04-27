USE dbms_vanminh;

-- Thêm dòng này để có thể chạy lại file nhiều lần mà không bị lỗi
DROP TRIGGER IF EXISTS trg_Upgrade_VIP;

DELIMITER / /

CREATE TRIGGER trg_Upgrade_VIP
AFTER UPDATE ON Bill
FOR EACH ROW
BEGIN
    DECLARE total_spent DECIMAL(12, 2);
    DECLARE total_tickets INT;

    -- Luồng này dành cho việc bấm nút "Thanh toán" trên Web (Update status từ 'Đang chờ' -> 'Đã thanh toán')
    IF NEW.status = 'Đã thanh toán' AND (OLD.status IS NULL OR OLD.status != 'Đã thanh toán') THEN
        
        -- 1. Tính tổng số tiền khách hàng đã chi trả
        SELECT SUM(total) INTO total_spent 
        FROM Bill 
        WHERE customer_id = NEW.customer_id AND status = 'Đã thanh toán';

        -- 2. Tính tổng số vé khách hàng đã đặt
        SELECT COUNT(t.tic_id) INTO total_tickets
        FROM Ticket t
        JOIN Bill b ON t.bill_id = b.bill_id
        WHERE b.customer_id = NEW.customer_id AND b.status = 'Đã thanh toán';

        -- 3. Tự động thăng hạng lên 'special'
        IF IFNULL(total_spent, 0) >= 5000000 OR total_tickets > 10 THEN
            UPDATE Customer 
            SET customer_type = 'special' 
            WHERE customer_id = NEW.customer_id;
        END IF;
        
    END IF;
END //

DELIMITER;