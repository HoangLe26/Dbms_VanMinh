USE dbms_vanminh;

DROP PROCEDURE IF EXISTS sp_LayLichSuTaiKhoan;

DELIMITER //

CREATE PROCEDURE sp_LayLichSuTaiKhoan(
    IN p_customer_id VARCHAR(50)
)
BEGIN
    SELECT
        b.bill_id,
        b.total,
        b.status,
        b.date        AS booking_date,
        b.method,
        dep_loc.province  AS dep_province,
        dep_loc.station   AS dep_station,
        arr_loc.province  AS arr_province,
        arr_loc.station   AS arr_station,
        t.dep_time,
        t.arr_time,
        GROUP_CONCAT(DISTINCT TRIM(s.seat_code) ORDER BY s.seat_code SEPARATOR ', ') AS seat_list
    FROM Bill b
    JOIN Ticket  tk  ON tk.bill_id  = b.bill_id
    JOIN Trip    t   ON t.trip_id   = tk.trip_id
    JOIN Location dep_loc ON dep_loc.loc_id = t.dep_sta_id
    JOIN Location arr_loc ON arr_loc.loc_id = t.arr_sta_id
    LEFT JOIN Ticket_Seat ts ON ts.tic_id   = tk.tic_id
    LEFT JOIN Seat        s  ON s.seat_id   = ts.seat_id
    WHERE b.customer_id = p_customer_id
    GROUP BY b.bill_id, b.total, b.status, b.date, b.method,
             dep_loc.province, dep_loc.station,
             arr_loc.province, arr_loc.station,
             t.dep_time, t.arr_time
    ORDER BY b.date DESC;
END //

DELIMITER ;
