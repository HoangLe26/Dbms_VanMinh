import mysql.connector

def ensure_seats():
    db = mysql.connector.connect(
        host="localhost",
        user="root", 
        password="2609", 
        database="dbms_vanminh"
    )
    cursor = db.cursor()
    
    # All possible seats we might need for 38 and 21 capacities
    needed_seats = []
    
    # For 38 seats layout: B1-B6, D1-D6, F1-F7, A1-A6, C1-C6, E1-E7
    for col in ['B', 'D']:
        for row in range(1, 7): needed_seats.append(f"{col}{row}")
    for row in range(1, 8): needed_seats.append(f"F{row}")
    
    for col in ['A', 'C']:
        for row in range(1, 7): needed_seats.append(f"{col}{row}")
    for row in range(1, 8): needed_seats.append(f"E{row}")
    
    # For 21 seats layout: A1-A7, B1-B7, C1-C7
    for col in ['A', 'B', 'C']:
        for row in range(1, 8): 
            seat = f"{col}{row}"
            if seat not in needed_seats:
                needed_seats.append(seat)
                
    # Also add D7, F7, etc if we just want a uniform 7x6 grid
    all_cols = ['A', 'B', 'C', 'D', 'E', 'F']
    for col in all_cols:
        for row in range(1, 8):
            seat = f"{col}{row}"
            if seat not in needed_seats:
                needed_seats.append(seat)
                
    cursor.execute("SELECT seat_code FROM Seat")
    existing_seats = [row[0].strip() for row in cursor.fetchall()]
    
    added_count = 0
    for seat in needed_seats:
        if seat not in existing_seats:
            # Generate a new SEAT_XXX id
            cursor.execute("SELECT MAX(CAST(SUBSTRING(seat_id, 6) AS UNSIGNED)) FROM Seat")
            max_id = cursor.fetchone()[0] or 0
            new_id = f"SEAT_{(max_id + 1):03d}"
            
            cursor.execute("INSERT INTO Seat (seat_id, seat_code) VALUES (%s, %s)", (new_id, seat))
            existing_seats.append(seat)
            added_count += 1
            
    db.commit()
    print(f"Added {added_count} new seats to the database.")
    
    cursor.close()
    db.close()

if __name__ == "__main__":
    ensure_seats()
