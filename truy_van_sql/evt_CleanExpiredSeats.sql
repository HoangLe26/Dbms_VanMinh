USE dbms_vanminh;

-- Bật MySQL Event Scheduler (cần chạy một lần)
SET GLOBAL event_scheduler = ON;

-- Xóa event cũ nếu có để chạy lại file không bị lỗi
DROP EVENT IF EXISTS evt_CleanExpiredSeats;

DELIMITER //

-- =====================================================================
-- evt_CleanExpiredSeats
-- Chạy mỗi 5 phút: xóa Ticket_Seat của các Bill "Đang chờ" đã hết hạn
-- (Quá 15 phút kể từ khi tạo → coi như khách bỏ qua, giải phóng ghế)
-- =====================================================================
CREATE EVENT evt_CleanExpiredSeats
ON SCHEDULE EVERY 5 MINUTE
STARTS NOW()
DO
    DELETE ts
    FROM   Ticket_Seat ts
    INNER JOIN Ticket tk ON ts.tic_id = tk.tic_id
    INNER JOIN Bill   b  ON tk.bill_id = b.bill_id
    WHERE  b.status = 'Đang chờ'
    AND    b.date   < NOW() - INTERVAL 15 MINUTE;

DELIMITER ;
