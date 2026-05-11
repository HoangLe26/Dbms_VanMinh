USE dbms_vanminh;

INSERT INTO
    Customer (
        customer_id,
        name,
        username,
        password,
        phonenum,
        email,
        customer_type
    )
VALUES (
        'ADMIN_001',
        'Hoàng Lê',
        'adminHoang',
        '123456',
        '0912345678',
        'hoang.admin@vanminh.com',
        'special'
    ),
    (
        'ADMIN_002',
        'Khải Vũ',
        'adminKhai',
        '123456',
        '0912345677',
        'hoang.admin@vanminh.com',
        'special'
    ),
    (
        'ADMIN_003',
        'Nguyễn Tùng',
        'adminTung',
        '123456',
        '0988888888',
        'tung.admin@vanminh.com',
        'special'
    );