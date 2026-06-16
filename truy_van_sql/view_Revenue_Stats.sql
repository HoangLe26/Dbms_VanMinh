USE dbms_vanminh;

-- =======================================================
-- VIEW 1: Thống kê doanh thu theo từng tháng
-- Gom nhóm hóa đơn đã thanh toán theo năm và tháng,
-- tính tổng doanh thu và số lượng hóa đơn mỗi tháng.
-- =======================================================
CREATE OR REPLACE VIEW vw_Revenue_By_Month AS
SELECT
    YEAR(b.date)                        AS nam,
    MONTH(b.date)                       AS thang,
    DATE_FORMAT(b.date, '%m/%Y')        AS thang_hien_thi,
    SUM(b.total)                        AS doanh_thu,
    COUNT(DISTINCT b.bill_id)           AS so_hoa_don,
    COUNT(DISTINCT tk.tic_id)           AS so_ve
FROM Bill b
JOIN Ticket tk ON b.bill_id = tk.bill_id
WHERE b.status = 'Đã thanh toán'
GROUP BY YEAR(b.date), MONTH(b.date), DATE_FORMAT(b.date, '%m/%Y')
ORDER BY nam DESC, thang DESC;


-- =======================================================
-- VIEW 2: Top tuyến xe bán chạy nhất
-- Gom nhóm theo tuyến đường (điểm đi -> điểm đến),
-- đếm số vé đã bán và tính tổng doanh thu của mỗi tuyến.
-- =======================================================
CREATE OR REPLACE VIEW vw_Top_Routes AS
SELECT
    l1.province                         AS tinh_di,
    l2.province                         AS tinh_den,
    CONCAT(l1.province, ' → ', l2.province) AS tuyen_duong,
    COUNT(DISTINCT b.bill_id)           AS so_luot_dat,
    COUNT(DISTINCT tk.tic_id)           AS so_ve_ban,
    SUM(b.total)                        AS doanh_thu
FROM Bill b
JOIN Ticket  tk ON b.bill_id    = tk.bill_id
JOIN Trip    t  ON tk.trip_id   = t.trip_id
JOIN Location l1 ON t.dep_sta_id = l1.loc_id
JOIN Location l2 ON t.arr_sta_id = l2.loc_id
WHERE b.status = 'Đã thanh toán'
GROUP BY l1.province, l2.province, CONCAT(l1.province, ' → ', l2.province)
ORDER BY so_ve_ban DESC;
