import psycopg2

# PostgreSQL 연결 설정
conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="######",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

#교통정보 출력
def get_traffic_information():
    try:
        cursor.execute("SELECT * FROM TrafficInformation ORDER BY informationID")
        traffic_info = cursor.fetchall()
        return traffic_info
    except psycopg2.Error as e:
        print("교통 정보 조회 중 오류 발생:", e)
        return None

#교통 정보 출력
def print_traffic_information():
    traffic_info = get_traffic_information()
    if traffic_info:
        print("{:<5} {:<20} {:<20} {:<20} {:<20} {:<20}".format(
            "ID", "City ID", "Traffic Data", "Collection Date", "Public Transport ID", "Manager ID"
        ))
        for info in traffic_info:
            # 교통 정보가 비어있는 경우 "-"로 대체하여 출력
            formatted_info = [("-" if val is None else val) for val in info]
            print("{:<5} {:<20} {:<20} {:<20} {:<20} {:<20}".format(*formatted_info))
    else:
        print("교통 정보가 없습니다.")

#교통 정보 추가
def add_traffic_information():
    try:
        print_table_contents("City")
        city_id = int(input("도시 ID를 입력하세요: "))
        traffic_data = input("교통 데이터를 입력하세요: ")
        collection_date = input("수집 날짜를 입력하세요 (YYYY-MM-DD 형식): ")
        print_table_contents("PublicTransportInformation")
        public_transport_id = int(input("대중교통 ID를 입력하세요: "))
        user_id = input("관리자 ID를 입력하세요: ")

        cursor.execute("INSERT INTO TrafficInformation (cityID, trafficData, collectionDate, publicTransportID, userID) VALUES (%s, %s, %s, %s, %s)",
                       (city_id, traffic_data, collection_date, public_transport_id, user_id))
        conn.commit()
        print("교통 정보 추가 완료!")
    except psycopg2.Error as e:
        conn.rollback()
        print("교통 정보 추가 중 오류 발생:", e)


#교통 수정 함수

def update_traffic_information():
    information_id = input("수정할 교통 정보의 ID를 입력하세요: ")
    new_city_id = input("새로운 도시 ID를 입력하세요: ")
    new_traffic_data = input("새로운 교통 데이터를 입력하세요: ")
    new_collection_date = input("새로운 수집 날짜를 입력하세요: ")
    new_public_transport_id = input("새로운 공공 교통 ID를 입력하세요: ")
    new_user_id = input("새로운 매니저 ID를 입력하세요: ")
    try:
        cursor.execute("SELECT * FROM TrafficInformation WHERE informationID = %s FOR UPDATE", (information_id,))
        # informationID에 해당하는 레코드를 잠금 설정

        cursor.execute("""
            UPDATE TrafficInformation 
            SET cityID = %s, trafficData = %s, collectionDate = %s, publicTransportID = %s, userID = %s
            WHERE informationID = %s
        """, (new_city_id, new_traffic_data, new_collection_date, new_public_transport_id, new_user_id, information_id))
        conn.commit()
        print("교통 정보 수정 완료!")
    except psycopg2.Error as e:
        conn.rollback()
        print("교통 정보 수정 중 오류 발생:", e)


#교통 정보 삭제
def delete_traffic_information_by_input():
    information_ids = input("삭제할 교통 정보의 ID를 입력하세요 (쉼표로 구분하여 여러 개 입력 가능): ").split(',')
    information_ids = [int(information_id.strip()) for information_id in information_ids if information_id.strip().isdigit()]

    try:
        if not information_ids:
            print("삭제할 교통 정보의 유효한 ID를 입력하세요.")
            return

        cursor.execute("DELETE FROM TrafficInformation WHERE informationID IN %s", (tuple(information_ids),))
        conn.commit()

        if len(information_ids) == 1:
            print(f"교통 정보 {information_ids[0]} 삭제 완료!")
        else:
            print(f"교통 정보 {', '.join(str(inf_id) for inf_id in information_ids)} 삭제 완료!")
    except psycopg2.Error as e:
        conn.rollback()
        print("교통 정보 삭제 중 오류 발생:", e)


#대중 교통 정보 조회
def get_public_transport_by_condition():
    try:
        transport_type = input("대중교통 유형을 입력하세요 (지하철 또는 버스): ")
        if transport_type not in ["지하철", "버스"]:
            print("잘못된 대중교통 유형입니다.")
            return None

        order_by = input(f"{transport_type}의 정렬 방식을 선택하세요 (route, schedule, station, status): ")
        if order_by not in ["route", "schedule", "station", "status"]:
            print("잘못된 정렬 방식입니다.")
            return None

        query = ""
        if transport_type == "지하철":
            query = f"SELECT * FROM PublicTransportInformation WHERE transportType = '지하철' ORDER BY {order_by}"
        elif transport_type == "버스":
            query = f"SELECT * FROM PublicTransportInformation WHERE transportType = '버스' ORDER BY {order_by}"

        cursor.execute(query)
        public_transport_info = cursor.fetchall()

        if public_transport_info:
            print("{:<5} {:<20} {:<20} {:<20} {:<20} {:<20}".format(
                "ID", "Transport Type", "Route", "Schedule", "Station", "Status"
            ))
            for info in public_transport_info:
                print("{:<5} {:<20} {:<20} {:<20} {:<20} {:<20}".format(
                    info[0], info[1], info[2], info[3], info[4], info[5]
                ))
        else:
            print("해당 조건의 대중교통 정보가 없습니다.")
    except psycopg2.Error as e:
        print("대중교통 정보 조회 중 오류 발생:", e)

# 긴급 상황 메시지 조회 함수
def get_emergency_message():
    cursor.execute("SELECT message FROM EmergencyMessages WHERE id = 1")
    message = cursor.fetchone()
    if message:
        print(message[0])
    else:
        print("-")

# 긴급 상황 메시지 업데이트 함수
def update_emergency_message():
    new_message = input("새로운 긴급 상황 메시지를 입력하세요: ")

    try:
        cursor.execute("BEGIN")  # 트랜잭션 시작

        cursor.execute("SELECT message FROM EmergencyMessages WHERE id = 1 FOR UPDATE")  # 레코드 잠금 설정
        message = cursor.fetchone()

        if message:
            cursor.execute("UPDATE EmergencyMessages SET message = %s WHERE id = 1", (new_message,))
        else:
            cursor.execute("INSERT INTO EmergencyMessages (id, message) VALUES (1, %s)", (new_message,))
        conn.commit()  # 트랜잭션 커밋
        print("긴급 상황 메시지 업데이트 완료!")
    except psycopg2.Error as e:
        conn.rollback()  # 롤백, 오류 시 변경 사항 취소
        print("긴급 상황 메시지 업데이트 중 오류 발생:", e)


# 긴급 상황 메시지 초기화 함수
def clear_emergency_message():
    cursor.execute("DELETE FROM EmergencyMessages")
    conn.commit()
######################
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
        ##################################3

def traffic_menu():
    while True:
        print("메뉴")
        print("1. 교통 정보 조회")
        print("2. 교통 정보 수정")
        print("3. 대중 교통 정보 조회")
        print("4. 긴급 상황 정보 수정")
        print("0. 종료")
        choice = input("번호를 입력하세요: ")

        if choice == "1":
            print_traffic_information() #교통 정보 조회
        elif choice == "2":
            # 시설 정보 수정 함수 호출
            show_traffic_update_menu()
            pass
        elif choice == "3":
            get_public_transport_by_condition() #대중 교통 정보 조회
        elif choice == "4":
            show_emergency_update_menu() # 긴급 상황 정보
        elif choice == "0":
            return
        else:
            print("잘못된 입력입니다. 다시 입력해주세요.")


def show_traffic_update_menu():
    while True:
        print("메뉴")
        print("1. 교통 정보 추가")
        print("2. 교통 정보 변경")
        print("3. 교통 정보 삭제")
        print("0. 종료")
        choice = input("번호를 입력하세요: ")

        if choice == "1":
            add_traffic_information()
            traffic_menu()
        elif choice == "2":
            print_traffic_information()
            update_traffic_information()
            print_traffic_information()
            traffic_menu()
        elif choice == "3":
            print_traffic_information()
            delete_traffic_information_by_input()
            print_traffic_information()
            traffic_menu()
        elif choice == "0":
            break
        else:
            print("잘못된 입력입니다. 다시 입력해주세요.")

def show_emergency_update_menu():
    while True:
        print("메뉴")
        print("1. 긴급 상황 정보 조회")
        print("2. 긴급 상황 정보 수정")
        print("3. 긴급 상황 정보 삭제")
        print("0. 종료")
        choice = input("번호를 입력하세요: ")

        if choice == "1":
            get_emergency_message()
            traffic_menu()
        elif choice == "2":
            update_emergency_message()
            get_emergency_message()
            traffic_menu()
        elif choice == "3" :
            clear_emergency_message()
            traffic_menu()
        elif choice == "0":
            break
        else:
            print("잘못된 입력입니다. 다시 입력해주세요.")
# 변경사항 저장
conn.commit()