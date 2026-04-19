CREATE OR REPLACE VIEW vw_Trip_Details AS
SELECT
    t.trip_id, t.dep_time, t.arr_time, t.duration, t.type, t.price, t.license_plate,
    dep_loc.station AS dep_station, dep_loc.province AS dep_province,
    arr_loc.station  AS arr_station, arr_loc.province AS arr_province,
    b.capacity,
    
    -- Lấy danh sách mã ghế ĐÃ MUA (Màu đỏ)
    (SELECT GROUP_CONCAT(s.seat_code) 
     FROM Ticket_Seat ts 
     JOIN Ticket tk ON ts.tic_id = tk.tic_id 
     JOIN Seat s ON ts.seat_id = s.seat_id
     JOIN Bill bl ON tk.bill_id = bl.bill_id 
     WHERE tk.trip_id = t.trip_id AND bl.status = 'Đã thanh toán') AS sold_seats_str,
    
    -- Lấy danh sách mã ghế ĐANG GIỮ (Màu vàng - Dưới 60s)
    (SELECT GROUP_CONCAT(s.seat_code) 
     FROM Ticket_Seat ts 
     JOIN Ticket tk ON ts.tic_id = tk.tic_id 
     JOIN Seat s ON ts.seat_id = s.seat_id
     JOIN Bill bl ON tk.bill_id = bl.bill_id 
     WHERE tk.trip_id = t.trip_id 
       AND bl.status = 'Đang chờ' 
       AND bl.date >= NOW() - INTERVAL 60 SECOND) AS pending_seats_str,
       
    -- Đếm tổng số ghế ĐÃ BỊ CHIẾM (gồm cả Đã mua + Đang giữ dưới 60s)
    (SELECT COUNT(*) 
     FROM Ticket_Seat ts 
     JOIN Ticket tk ON ts.tic_id = tk.tic_id 
     JOIN Bill bl ON tk.bill_id = bl.bill_id 
     WHERE tk.trip_id = t.trip_id 
       AND (bl.status = 'Đã thanh toán' OR (bl.status = 'Đang chờ' AND bl.date >= NOW() - INTERVAL 60 SECOND))
    ) AS occupied_seats_count
    
FROM Trip t
JOIN Location dep_loc ON t.dep_sta_id = dep_loc.loc_id
JOIN Location arr_loc ON t.arr_sta_id = arr_loc.loc_id
JOIN Bus b ON t.license_plate = b.license_plate;
