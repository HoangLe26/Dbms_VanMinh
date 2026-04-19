import mysql.connector

def create_trigger():
    print("Đang kết nối đến cơ sở dữ liệu...")
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root", 
            password="2609", 
            database="dbms_vanminh"
        )
        cursor = db.cursor()
        
        # Lệnh SQL tạo Trigger kiểm tra thời gian khởi hành
        sql_create_trigger = """
        CREATE TRIGGER trg_Prevent_Late_Booking 
        BEFORE INSERT ON Ticket
        FOR EACH ROW
        BEGIN
            DECLARE trip_departure DATETIME;
            
            -- Lấy thời gian khởi hành của chuyến xe đang được đặt vé
            SELECT dep_time INTO trip_departure 
            FROM Trip 
            WHERE trip_id = NEW.trip_id;
            
            -- Kiểm tra: Nếu thời gian hiện tại đã vượt quá thời gian khởi hành
            IF NOW() > trip_departure THEN
                -- Báo lỗi và HUỶ luôn thao tác INSERT (Không cho đặt vé nữa)
                SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Lỗi: Chuyến xe này đã khởi hành, không thể đặt thêm vé!';
            END IF;
        END;
        """
        
        print("Đang tạo Trigger 'trg_Prevent_Late_Booking'...")
        # Bỏ qua lỗi nếu trigger đã tồn tại để tạo lại
        try:
            cursor.execute("DROP TRIGGER IF EXISTS trg_Prevent_Late_Booking")
        except:
            pass
            
        cursor.execute(sql_create_trigger)
        db.commit()
        print("✅ Thành công! Đã tạo Trigger trg_Prevent_Late_Booking trong cơ sở dữ liệu MySQL.")
        
    except mysql.connector.Error as err:
        print(f"❌ Lỗi: {err}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    create_trigger()
