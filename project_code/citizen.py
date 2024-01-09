import psycopg2
from datetime import datetime

# PostgreSQL 연결 설정
conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="######",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

# 긴급 상황 메시지 조회 함수
def get_emergency_message():
    cursor.execute("SELECT message FROM EmergencyMessages WHERE id = 1")
    message = cursor.fetchone()
    if message:
        print(message[0])
    else:
        print("-")

#교통 정보 조회 테이블
def query_traffic_information():
    try:
        # 존재하는 교통 정보 ID 목록 조회
        cursor.execute("SELECT informationID FROM TrafficInformation")
        existing_ids = cursor.fetchall()

        if not existing_ids:
            print("존재하는 교통 정보가 없습니다.")
            return

        print("존재하는 교통 정보 ID 목록:", existing_ids)

        user_id = input("사용자 ID를 입력하세요: ")  # 사용자 ID 입력
        information_id = int(input("교통 정보 ID를 입력하세요: "))  # 교통 정보 ID 입력

        # 현재 시간을 timestamp로 가져오기
        current_timestamp = datetime.now()

        # TrafficQuery 테이블에 조회 기록 추가
        cursor.execute("INSERT INTO TrafficQuery (userID, informationID, queryDate) VALUES (%s, %s, %s)",
                       (user_id, information_id, current_timestamp))
        conn.commit()

        # 교통 정보 조회
        cursor.execute("SELECT * FROM TrafficInformation WHERE informationID = %s", (information_id,))
        traffic_info = cursor.fetchone()

        # 조회된 정보를 출력하거나 다른 작업 수행
        if traffic_info:
            print(f"조회된 교통 정보: {traffic_info}")
            print("*참고 : (informationID, cityID, trafficData, collectionDate, publicTransportID, userID)")
        else:
            print("해당 ID에 대한 교통 정보가 없습니다.")

    except (psycopg2.Error, ValueError) as e:
        conn.rollback()
        print("교통 정보 조회 중 오류 발생:", e)



# 시설 정보 조회 함수
def get_facility_information():
    try:
        cursor.execute("SELECT * FROM Facility ORDER BY facilityID")
        facility_info = cursor.fetchall()
        return facility_info
    except psycopg2.Error as e:
        print("시설 정보 조회 중 오류 발생:", e)
        return None
# 시설 정보 출력 함수
def print_facility_information():
    facility_info = get_facility_information()
    if facility_info:
        print("{:<5} {:<20} {:<20} {:<20}".format("ID", "이름", "유형", "위치"))
        for facility in facility_info:
            print("{:<5} {:<20} {:<20} {:<20}".format(facility[0], facility[1], facility[2], facility[3]))
    else:
        print("시설 정보가 없습니다.")

# 시설 운영 일정 조회
def get_facility_operations():
    try:
        cursor.execute("SELECT f.facilityID, f.facilityName, fo.startDate, fo.endDate, fo.dayOfWeek, fo.userID FROM Facility f LEFT JOIN FacilityOperation fo ON f.facilityID = fo.facilityID")
        operations = cursor.fetchall() or []

        # 운영 일정이 없는 경우에 대한 추가 처리
        operations_with_info = []
        for op in operations:
            operation_info = list(op)
            if None in operation_info[2:]:  # 운영 일정 정보가 없는 경우
                operation_info[2:] = ["-", "-", "-"]  # 기본값으로 설정
            operations_with_info.append(tuple(operation_info))

        return operations_with_info
    except psycopg2.Error as e:
        print("시설 운영 일정 조회 중 오류 발생:", e)
        return []

def print_facility_information_with_operations():
    facilities = get_facility_information()
    operations = get_facility_operations()

    if facilities is None or operations is None:
        print("시설 정보 또는 운영 일정 정보를 가져올 수 없습니다.")
        #return

    print("{:<5} {:<20} {:<20} {:<20} {:<20} {:<20} {:<20}".format("ID", "이름", "유형", "위치", "시작일", "종료일", "요일"))

    for facility in facilities:
        facility_id = facility[0]
        matching_operations = [op for op in operations if op[0] == facility_id]

        if matching_operations:
            for operation in matching_operations:
                start_date, end_date, day_of_week = operation[2], operation[3], operation[4]
                print("{:<5} {:<20} {:<20} {:<20} {:<20} {:<20} {:<20}".format(
                    facility[0], facility[1], facility[2], facility[3], start_date, end_date, day_of_week
                ))
        else:
            print("{:<5} {:<20} {:<20} {:<20} {:<20} {:<20} {:<20}".format(
                facility[0], facility[1], facility[2], facility[3], "-", "-", "-"
            ))
#시설 예약
def create_reservation():
    facility_id = int(input("시설 ID를 입력하세요: "))
    user_id = input("사용자 ID를 입력하세요: ")
    reservation_date = input("예약 날짜를 입력하세요 (YYYY-MM-DD 형식): ")
    reservation_time = input("예약 시간을 입력하세요 (HH:MM 형식): ")

    try:
        cursor.execute("SELECT availableSlots FROM Facility WHERE facilityID = %s FOR UPDATE", (facility_id,))
        available_slots = cursor.fetchone()[0]

        if available_slots > 0:
            cursor.execute("""
                INSERT INTO FacilityReservation (facilityID, userID, reservationDate, reservationTime, status) 
                VALUES (%s, %s, %s, %s, %s) RETURNING reservationID
            """, (facility_id, user_id, reservation_date, reservation_time, "Confirmed"))

            reservation_id = cursor.fetchone()[0]  # 예약의 ID를 변수에 저장
            conn.commit()

            cursor.execute("UPDATE Facility SET availableSlots = availableSlots - 1 WHERE facilityID = %s", (facility_id,))
            conn.commit()

            print(f"예약이 완료되었습니다. 예약 ID는 {reservation_id}입니다.")
        else:
            print("죄송합니다. 해당 시설은 예약이 모두 차있습니다.")

    except psycopg2.Error as e:
        conn.rollback()
        print("예약 중 오류 발생:", e)


# 시설 예약 취소
def cancel_reservation():

    reservation_id = int(input("취소할 예약의 ID를 입력하세요: "))

    try:
        cursor.execute("SELECT facilityID FROM FacilityReservation WHERE reservationID = %s", (reservation_id,))
        reservation = cursor.fetchone()

        if reservation:
            facility_id = reservation[0]

            cursor.execute("DELETE FROM FacilityReservation WHERE reservationID = %s", (reservation_id,))
            conn.commit()

            cursor.execute("UPDATE Facility SET availableSlots = availableSlots + 1 WHERE facilityID = %s", (facility_id,))
            conn.commit()

            print("예약이 취소되었습니다.")
        else:
            print("해당하는 예약이 존재하지 않습니다. 다시 확인해주세요.")
    except psycopg2.Error as e:
        conn.rollback()
        print("예약 취소 중 오류 발생:", e)


#시설 평가
def add_facility_review():
    user_id = input("사용자의 ID를 입력하세요: ")
    print_facility_information()
    facility_id = int(input("평가할 시설의 ID를 입력하세요: "))

    try:
        # 해당 사용자가 시설을 예약했는지 확인
        cursor.execute("SELECT COUNT(*) FROM FacilityReservation WHERE userID = %s AND facilityID = %s", (user_id, facility_id))
        reservation_count = cursor.fetchone()[0]

        if reservation_count > 0:
            rating_input = input("평점을 입력하세요 (0부터 5까지), 입력하지 않으면 엔터: ")
            review = input("리뷰를 입력하세요, 없으면 엔터: ")

            # 사용자 입력을 처리하고, 디폴트 값 처리
            rating = float(rating_input) if rating_input else 0
            review = review if review else ""

            # 예약한 사용자만 평가 등록
            cursor.execute("INSERT INTO FacilityReview (facilityID, userID, rating, comment) VALUES (%s, %s, %s, %s)",
                           (facility_id, user_id, rating, review))
            conn.commit()
            print("평가와 리뷰가 등록되었습니다.")
        else:
            print("해당 시설을 예약한 사용자만 평가할 수 있습니다.")

    except psycopg2.Error as e:
        conn.rollback()
        print("평가 등록 중 오류 발생:", e)

###########################################
def citizen_menu():
    print("---------긴급상황-----------")
    get_emergency_message()
    print("--------------------------")
    while True:
        print("메뉴")
        print("1. 시설 정보 조회")
        print("2. 시설 운영 정보 조회")
        print("3. 시설 예약")
        print("4. 시설 평가")
        print("5. 교통 정보 조회")
        print("0. 종료")
        choice = input("번호를 입력하세요: ")

        if choice == "1":
            print_facility_information()
        elif choice == "2":
            print_facility_information_with_operations()
        elif choice == "3":
            show_reservation_menu()
        elif choice == "4":
            add_facility_review()
        elif choice == "5":
            query_traffic_information()
        elif choice == "0":
            return
        else :
            print("잘못된 입력입니다. 다시 입력해주세요.")

def show_reservation_menu():
    while True:
        print("메뉴")
        print("1. 시설 예약")
        print("2. 시설 예약 취소")
        print("0. 뒤로 가기")
        choice = input("번호를 입력하세요: ")

        if choice == "1":
            print_facility_information_with_operations()
            create_reservation()
            citizen_menu()
        elif choice == "2":
            cancel_reservation()
            citizen_menu()
        elif choice == "0":
            citizen_menu()
            break
        else :
            print("잘못된 입력입니다. 다시 입력해주세요.")
# 변경사항 저장
conn.commit()