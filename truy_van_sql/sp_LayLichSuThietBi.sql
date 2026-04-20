DELIMITER $$

CREATE PROCEDURE sp_LayLichSuThietBi(
    IN p_bill_list VARCHAR(2000)
)
BEGIN
   
    SELECT 
        b.bill_id,
        b.status,
        b.total,
        b.date AS booking_date,
        t.dep_time,
        t.arr_time,
        t.type AS bus_type,
        dep_loc.station AS dep_station,
        dep_loc.province AS dep_province,
        arr_loc.station AS arr_station,
        arr_loc.province AS arr_province,
        
        GROUP_CONCAT(s.seat_code ORDER BY s.seat_code SEPARATOR ', ') AS seat_list
    FROM Bill b
    JOIN Ticket tk ON b.bill_id = tk.bill_id
    JOIN Trip t ON tk.trip_id = t.trip_id
    JOIN Location dep_loc ON t.dep_sta_id = dep_loc.loc_id
    JOIN Location arr_loc ON t.arr_sta_id = arr_loc.loc_id
    JOIN Ticket_Seat ts ON tk.tic_id = ts.tic_id
    JOIN Seat s ON ts.seat_id = s.seat_id
    
    
    WHERE FIND_IN_SET(b.bill_id, p_bill_list) > 0
    
    GROUP BY 
        b.bill_id, b.status, b.total, b.date, 
        t.dep_time, t.arr_time, t.type,
        dep_loc.station, dep_loc.province, 
        arr_loc.station, arr_loc.province
        
    -- Sắp xếp luôn từ CSDL: Mới mua lên đầu
    ORDER BY b.date DESC;
    
END$$

DELIMITER ;
