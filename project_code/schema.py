import psycopg2

def create_tables():
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="######",
        host="localhost",
        port="5432"
    )
    cursor = conn.cursor()

    # 기존 City 테이블 삭제
    cursor.execute('DROP TABLE IF EXISTS City CASCADE')
    # City 테이블 생성
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS City (
            cityID SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            country TEXT NOT NULL
        )
    ''')

    # City 테이블에 데이터 추가
    cities = [
        (1, '서울', '대한민국'),
        (2, '부산', '대한민국'),
        (3, '대구', '대한민국'),
        (4, '대전', '대한민국'),
        (5, '광주', '대한민국'),
        (6, '울산', '대한민국')
    ]

    for city in cities:
        cursor.execute("INSERT INTO City (cityID, name, country) VALUES (%s, %s, %s)", city)

    # User 테이블 생성
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            userID TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')

    # FacilityManager 테이블 생성
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS FacilityManager (
            managerID SERIAL PRIMARY KEY,
            userID TEXT NOT NULL REFERENCES Users(userID),
            name TEXT,
            position TEXT,
            phone TEXT,
            managedCityID INT,
            FOREIGN KEY (managedCityID) REFERENCES City(cityID)
        )
    ''')

    # Citizen 테이블 생성
    cursor.execute('''
         CREATE TABLE IF NOT EXISTS Citizen (
            citizenID SERIAL PRIMARY KEY,
            userID TEXT NOT NULL REFERENCES Users(userID),
            name TEXT,
            address TEXT,
            phone TEXT
        )
    ''')

    # TrafficManager 테이블 생성
    cursor.execute('''
         CREATE TABLE IF NOT EXISTS TrafficManager (
            managerID SERIAL PRIMARY KEY,
            userID TEXT NOT NULL REFERENCES Users(userID),
            name TEXT,
            position TEXT,
            phone TEXT,
            managedCityID INT,
            FOREIGN KEY (managedCityID) REFERENCES City(cityID)
        )
    ''')


    # Facility 테이블 생성
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Facility (
            facilityID SERIAL PRIMARY KEY,
            facilityName TEXT NOT NULL,
            facilityType TEXT,
            location TEXT,
            availableSlots INT DEFAULT 5 
        )
    ''')

    # FacilityOperation 테이블 생성
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS FacilityOperation (
            scheduleID SERIAL PRIMARY KEY,
            facilityID INT,
            startDate TEXT,
            endDate TEXT,
            dayofWeek TEXT,
            userID TEXT,
            FOREIGN KEY (facilityID) REFERENCES Facility(facilityID),
            FOREIGN KEY (userID) REFERENCES Users(userID)
        )
    ''')

    # FacilityReservation 테이블 생성
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS FacilityReservation (
            reservationID SERIAL PRIMARY KEY,
            facilityID INT,
            userID TEXT,
            reservationDate DATE,
            reservationTime TIME,
            status TEXT,
            FOREIGN KEY (facilityID) REFERENCES Facility(facilityID),
            FOREIGN KEY (userID) REFERENCES Users(userID)
        )
    ''')

    # FacilityReview 테이블 생성
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS FacilityReview (
            reviewID SERIAL PRIMARY KEY,
            facilityID INT,
            userID TEXT,
            rating FLOAT,
            comment TEXT,
            FOREIGN KEY (facilityID) REFERENCES Facility(facilityID),
            FOREIGN KEY (userID) REFERENCES Users(userID)
        )
    ''')

    # TrafficInformation 테이블 생성
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS TrafficInformation (
            informationID SERIAL PRIMARY KEY,
            cityID INT,
            trafficData TEXT,
            collectionDate TEXT,
            publicTransportID INT,
            userID TEXT,
            FOREIGN KEY (cityID) REFERENCES City(cityID),
            FOREIGN KEY (publicTransportID) REFERENCES PublicTransportInformation(transportID),
            FOREIGN KEY (userID) REFERENCES Users(userID)
        )
    ''')

    # TrafficQuery 테이블 생성
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS TrafficQuery (
            queryID SERIAL PRIMARY KEY,
            userID TEXT,
            informationID INT,
            queryDate DATE,
            FOREIGN KEY (userID) REFERENCES Users(userID),
            FOREIGN KEY (informationID) REFERENCES TrafficInformation(informationID)
        )
    ''')

    # 긴급 상황 메시지 테이블 생성
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS EmergencyMessages (
            id SERIAL PRIMARY KEY,
            message TEXT
        )
    ''')

    # PublicTransportInformation 테이블 생성
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS PublicTransportInformation (
            transportID SERIAL PRIMARY KEY,
            transportType TEXT,
            route TEXT,
            schedule TEXT,
            station TEXT,
            status TEXT
        )
    ''')

    transport_data = [
        ('지하철', '2호선', '매 10분 간격', '서면역', '운행 중'),
        ('지하철', '3호선', '매 8분 간격', '사상역', '운행 중'),
        ('버스', '서면>수영', '매 30분 간격', '수영', '운행 중'),
        ('버스', '수영>대저', '매 20분 간격', '사직', '운행 중')
    ]

    for transport_info in transport_data:
        cursor.execute(
            "INSERT INTO PublicTransportInformation (transportType, route, schedule, station, status) "
            "SELECT %s, %s, %s, %s, %s "
            "WHERE NOT EXISTS (SELECT 1 FROM PublicTransportInformation "
            "WHERE transportType = %s AND route = %s AND schedule = %s AND station = %s AND status = %s)",
            transport_info + transport_info
        )

    query = "ALTER SEQUENCE publictransportinformation_transportid_seq RESTART WITH 1;"
    cursor.execute(query)
    conn.commit()
    conn.close()