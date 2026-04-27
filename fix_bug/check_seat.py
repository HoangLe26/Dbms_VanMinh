import mysql.connector
db = mysql.connector.connect(host='localhost', user='root', password='2609', database='dbms_vanminh')
cursor = db.cursor()

# BILL_0037 co ghe E2, B3, C4 - nhung TRIP_0085 la xe Limousine 21 cho (chi co A,B,C col 1-7)
# E2 la ghe cua xe GIUONG NAM, khong phai Limousine!
# → Day la nguyen nhan so dem sai: ghe E2 cua xe khac nhung duoc dem vao Limousine

print('=== TRIP_0085 la loai xe gi? ===')
cursor.execute(
    'SELECT t.trip_id, t.type, b.capacity, b.bus_description '
    'FROM Trip t JOIN Bus b ON t.license_plate = b.license_plate '
    "WHERE t.trip_id = 'TRIP_0085'"
)
for r in cursor.fetchall():
    print(r)

print()
print('=== BILL_0037 - ghe E2 la ghe gi? ===')
cursor.execute(
    'SELECT b.bill_id, b.status, tk.trip_id, s.seat_code '
    'FROM Bill b '
    'JOIN Ticket tk ON tk.bill_id = b.bill_id '
    'JOIN Ticket_Seat ts ON ts.tic_id = tk.tic_id '
    'JOIN Seat s ON s.seat_id = ts.seat_id '
    "WHERE b.bill_id = 'BILL_0037'"
)
for r in cursor.fetchall():
    print(r)

print()
print('=== Kiem tra: Seat.seat_code co trung nhau khong? ===')
cursor.execute(
    'SELECT seat_code, COUNT(*) as so_lan '
    'FROM Seat '
    'GROUP BY seat_code '
    'HAVING COUNT(*) > 1'
)
dupes = cursor.fetchall()
if dupes:
    print('CO TRUNG: ', dupes)
else:
    print('Khong co seat_code nao trung nhau trong bang Seat')

print()
print('=== Kiem tra ROOT CAUSE: Seat khong co bus_type, tat ca chung toa xe dung chung bang Seat ===')
cursor.execute('SELECT COUNT(*) FROM Seat')
total = cursor.fetchone()[0]
print(f'Tong so row trong bang Seat: {total}')
cursor.execute('DESCRIBE Seat')
print('Cau truc bang Seat:')
for r in cursor.fetchall():
    print(' ', r)

print()
print('=== sp_LockSeats tim seat_id theo seat_code (khong loc theo loai xe!) ===')
print('Vi du: ghe C4 cua TRIP_0085 (Limousine) va BILL_0037 chia se chung 1 seat_id trong bang Seat')
print()
print('=== Kiem tra TRIP_0090 - chuyen co bill Dang cho qua han ===')
cursor.execute(
    'SELECT b.bill_id, b.status, b.date, '
    'TIMESTAMPDIFF(MINUTE, b.date, NOW()) as phut_da_qua, '
    'COUNT(ts.seat_id) as so_ghe '
    'FROM Bill b '
    'JOIN Ticket tk ON tk.bill_id = b.bill_id '
    'LEFT JOIN Ticket_Seat ts ON ts.tic_id = tk.tic_id '
    "WHERE tk.trip_id = 'TRIP_0090' "
    'GROUP BY b.bill_id, b.status, b.date'
)
for r in cursor.fetchall():
    print(r)

cursor.close()
db.close()
