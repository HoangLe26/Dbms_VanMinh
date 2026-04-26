SET FOREIGN_KEY_CHECKS = 0;  -- Tạm thời "bịt mắt" MySQL, tắt kiểm tra khóa ngoại
TRUNCATE TABLE Trip;         -- Xóa trắng bảng Trip thoải mái
SET FOREIGN_KEY_CHECKS = 1;  -- Mở mắt MySQL ra, bật lại kiểm tra khóa ngoạiQ