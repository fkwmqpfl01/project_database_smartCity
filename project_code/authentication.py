# authentication.py

import psycopg2

conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="######",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

MAX_LOGIN_ATTEMPTS = 3  # 최대 로그인 시도 횟수
LOCK_TIME = 10  # 잠금 시간(초)
def login_prompt():
    userID = input("사용자 ID를 입력하세요: ")
    password = input("비밀번호를 입력하세요: ")
    return userID, password

def register_prompt():
    userID = input("사용자 ID를 입력하세요: ")
    password = input("비밀번호를 입력하세요: ")
    role = input("역할(시설관리자, 시민, 교통관리자)을 선택하세요: ")  # 사용자 역할을 입력받음
    if role == '시설관리자':
        role = 'FacilityManager'
    elif role == '교통관리자':
        role = 'TrafficManager'
    elif role == '시민' :
        role = 'Citizen'
    return userID, password, role

def print_table_contents(table_name):
    try:
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()

        if rows:
            column_names = [desc[0] for desc in cursor.description]
            max_lengths = [max(len(str(row[i])) for row in rows) for i in range(len(column_names))]

            # Adjust the minimum column width
            min_column_width = 15

            # Print column headers
            for i, column_name in enumerate(column_names):
                width = max(max_lengths[i] + 12, min_column_width)  # Select the maximum between max length and minimum width
                print(f"{column_name: <{width}}", end="")

            print("\n" + "-" * sum(max_lengths))

            # Print table contents
            for row in rows:
                for i, value in enumerate(row):
                    width = max(max_lengths[i] + 10, min_column_width)  # Select the maximum between max length and minimum width
                    print(f"{value: <{width}}", end="")
                print()

        else:
            print("테이블 내용이 없습니다.")

    except psycopg2.Error as e:
        print("테이블 내용 출력 중 오류 발생:", e)

# 로그인 기능
def login(userID, password):
    try:
        cursor.execute("SELECT userID, role FROM users WHERE userID = %s AND password = %s", (userID, password))
        user_data = cursor.fetchone()

        if user_data:
            userID, role = user_data
            return userID, role  # 사용자 ID와 권한을 반환하거나 세션을 시작할 수 있음
        else:
            return None, None  # 로그인 실패
    except psycopg2.Error as e:
        print("로그인 중 오류 발생:", e)
        return None  # 오류 처리

def register_facility_manager():
    print("시설 관리자로 회원가입을 진행합니다.")
    name = input("이름을 입력하세요: ")
    position = input("직책을 입력하세요: ")
    phone = input("전화번호를 입력하세요: ")
    print_table_contents("City")
    managed_city_id = input("관리하는 도시 ID를 입력하세요: ")
    return name,position,phone,managed_city_id

def register_traffic_manager():
    print("교통 관리자로 회원가입을 진행합니다.")
   # manager_id = input("관리자 ID를 입력하세요: ")
    name = input("이름을 입력하세요: ")
    position = input("직책을 입력하세요: ")
    phone = input("전화번호를 입력하세요: ")
    print_table_contents("City")
    managed_city_id = input("관리하는 도시 ID를 입력하세요: ")
    return name,position,phone,managed_city_id

def register_citizen():
    print("시민으로 회원가입을 진행합니다.")
    name = input("이름을 입력하세요: ")
    address = input("주소를 입력하세요: ")
    phone = input("전화번호를 입력하세요: ")
    return name,address,phone

#회원가입 기능
def register(userID, password, role):
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="lucy0202",
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()

        cursor.execute("SELECT userID FROM Users WHERE userID = %s", (userID,))
        existing_user = cursor.fetchone()

        if existing_user:
            print("이미 존재하는 사용자 아이디입니다.")
            return None  # 사용자가 이미 존재하는 경우
        else:
            cursor.execute("INSERT INTO Users (userID, password, role) VALUES (%s, %s, %s)",
                           (userID, password, role))
            # FacilityManager 테이블에 추가 정보 삽입
            if role == 'FacilityManager':
                cursor.execute("INSERT INTO FacilityManager (userID) VALUES (%s)", (userID,))
                name, position, phone, managed_city_id = register_facility_manager()
                cursor.execute(
                    "INSERT INTO FacilityManager (userID, name, position, phone, managedCityID) VALUES (%s, %s, %s, %s, %s)",
                    (userID, name, position, phone, managed_city_id)
                )

            # TrafficManager 테이블에 추가 정보 삽입
            elif role == 'TrafficManager':
                cursor.execute("INSERT INTO TrafficManager (userID) VALUES (%s)", (userID,))
                name, position, phone, managed_city_id = register_traffic_manager()
                cursor.execute(
                    "INSERT INTO TrafficManager (userID, name, position, phone, managedCityID) VALUES (%s, %s, %s, %s, %s)",
                    (userID, name, position, phone, managed_city_id)
                )

            # Citizen 테이블에 추가 정보 삽입
            elif role == 'Citizen':
                cursor.execute("INSERT INTO Citizen (userID) VALUES (%s)", (userID,))
                name, address, phone = register_citizen()
                cursor.execute(
                    "INSERT INTO Citizen (userID, name, address, phone) VALUES (%s, %s, %s, %s)",
                    (userID, name, address, phone)
                )
            else :
                return None
            conn.commit()
            print("회원가입이 완료되었습니다. 사용자 ID:", userID)
            return userID  # 새로운 사용자의 ID 반환
    except psycopg2.Error as e:
        conn.rollback()
        print("회원가입 중 오류 발생:", e)
        return None  # 오류 처리
    finally:
        conn.close()

def login_menu():
    while True:
        print("1. 로그인")
        print("2. 회원가입")
        print("0. 종료")
        choice = input("번호를 입력하세요: ")

        if choice == '1':  # 로그인 선택
            userID, password = login_prompt()
            user, role = login(userID, password)
            if user:
                print("로그인 성공!")
                return userID, role
                break
                # 로그인에 성공하면 사용자 정보를 이용하여 다른 작업 수행
            else:
                print("로그인 실패!")
        elif choice == '2':  # 회원가입 선택
            userID, password, role = register_prompt()
            success = register(userID, password, role)
            if success:
                print("회원가입 성공!")
            else:
                print("회원가입 실패!")
        elif choice == '0':
            break
        else:
            print("올바른 숫자를 입력하세요.")
