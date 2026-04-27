USE dbms_vanminh;

DROP PROCEDURE IF EXISTS sp_LayThongTinCaNhan;

DELIMITER //

CREATE PROCEDURE sp_LayThongTinCaNhan(
    IN p_customer_id VARCHAR(50)
)
BEGIN
    SELECT name, customer_type, phonenum, email 
    FROM Customer 
    WHERE customer_id = p_customer_id 
    LIMIT 1;
END //

DELIMITER ;
