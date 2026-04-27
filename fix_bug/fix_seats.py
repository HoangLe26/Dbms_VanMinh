import mysql.connector
import re

db = mysql.connector.connect(host='localhost', user='root', password='2609', database='dbms_vanminh')
cursor = db.cursor()

stmts = [
    "SET GLOBAL event_scheduler = ON",
    "DROP EVENT IF EXISTS evt_CleanExpiredSeats",
    (
        "CREATE EVENT evt_CleanExpiredSeats "
        "ON SCHEDULE EVERY 5 MINUTE STARTS NOW() "
        "DO DELETE ts FROM Ticket_Seat ts "
        "INNER JOIN Ticket tk ON ts.tic_id = tk.tic_id "
        "INNER JOIN Bill b ON tk.bill_id = b.bill_id "
        "WHERE b.status = 'Dang cho' "
        "AND b.date < NOW() - INTERVAL 15 MINUTE"
    )
]

for stmt in stmts:
    try:
        cursor.execute(stmt)
        db.commit()
        print('OK:', stmt[:70])
    except Exception as e:
        print('ERR:', str(e)[:100])

# Xac nhan event da duoc tao
cursor.execute("SELECT event_name, status, interval_value, interval_field FROM information_schema.EVENTS WHERE event_schema = 'dbms_vanminh'")
events = cursor.fetchall()
print()
print('Events trong DB:')
for e in events:
    print(' ', e)

cursor.close()
db.close()
print('Done')
