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


#시설 추가 함수
def get_next_available_id():
    try:
        cursor.execute("SELECT MIN(facilityID) + 1 FROM Facility WHERE NOT EXISTS (SELECT 1 FROM Facility f WHERE f.facilityID = Facility.facilityID + 1)")
        next_id = cursor.fetchone()
        return next_id[0] if next_id[0] is not None else 1  # 새로운 ID 반환, 기존 데이터가 없으면 1 반환
    except psycopg2.Error as e:
        print("다음 사용 가능한 ID 조회 중 오류 발생:", e)
        return 1  # 오류 발생 시 1 반환

def add_facility():
    try:
        name = input("시설 이름을 입력하세요: ")
        f_type = input("시설 유형을 입력하세요: ")
        location = input("시설 위치를 입력하세요: ")
        next_id = get_next_available_id()  # 다음 사용 가능한 ID 조회
        cursor.execute("INSERT INTO Facility (facilityID, facilityName, facilityType, location) VALUES (%s, %s, %s, %s)",
                       (next_id, name, f_type, location))
        conn.commit()
        print("시설 추가 완료!")
    except psycopg2.Error as e:
        conn.rollback()
        print("시설 추가 중 오류 발생:", e)

#시설 수정
def update_facility():
    facility_id = input("수정할 시설의 ID를 입력하세요: ")
    new_name = input("새로운 시설 이름을 입력하세요: ")
    new_type = input("새로운 시설 유형을 입력하세요: ")
    new_location = input("새로운 시설 위치를 입력하세요: ")

    try:
        cursor.execute("SELECT * FROM Facility WHERE facilityID = %s FOR UPDATE", (facility_id,))
        existing_facility = cursor.fetchone()
        if existing_facility:
            cursor.execute("UPDATE Facility SET facilityName = %s, facilityType = %s, location = %s WHERE facilityID = %s",
                           (new_name, new_type, new_location, facility_id))
            conn.commit()
            print("시설 수정 완료!")
            print(f"시설 ID가 {facility_id}인 운영 일정/예약 사항을 확인하세요.")
        else:
            print("해당 ID의 시설이 존재하지 않습니다.")
    except psycopg2.Error as e:
        conn.rollback()
        print("시설 수정 중 오류 발생:", e)
    finally:
        cursor.execute("COMMIT")


#시설 삭제

def delete_facility_by_id():
    facility_ids = input("삭제할 시설의 ID를 입력하세요 (쉼표로 구분하여 여러 개 입력 가능): ").split(',')
    facility_ids = [int(fid.strip()) for fid in facility_ids if fid.strip().isdigit()]

    try:
        if not facility_ids:
            print("삭제할 시설의 유효한 ID를 입력하세요.")
            return

        for fid in facility_ids:
            cursor.execute("SELECT * FROM Facility WHERE facilityID = %s FOR UPDATE", (fid,))
            existing_facility = cursor.fetchone()
            if not existing_facility:
                print(f"시설 ID {fid}가 존재하지 않습니다.")
                return

            # 해당 시설과 관련된 운영 일정 확인
            cursor.execute("SELECT * FROM FacilityOperation WHERE facilityID = %s", (fid,))
            operation_schedule = cursor.fetchone()

            if operation_schedule:
                # 운영 일정이 존재하면 삭제
                cursor.execute("DELETE FROM FacilityOperation WHERE facilityID = %s", (fid,))

            # 해당 시설과 관련된 예약 정보 확인 후 삭제
            cursor.execute("DELETE FROM FacilityReservation WHERE facilityID = %s", (fid,))

            # 해당 시설과 관련된 평가 정보 확인 후 삭제
            cursor.execute("DELETE FROM FacilityReview WHERE facilityID = %s", (fid,))

        cursor.execute("DELETE FROM Facility WHERE facilityID IN %s", (tuple(facility_ids),))
        conn.commit()

        if len(facility_ids) == 1:
            print(f"시설 {facility_ids[0]} 삭제 완료!")
        else:
            print(f"시설 {', '.join(str(fid) for fid in facility_ids)} 삭제 완료!")
    except psycopg2.Error as e:
        conn.rollback()
        print("시설 삭제 중 오류 발생:", e)
    finally:
        cursor.execute("COMMIT")


# 시설 운영 일정 추가
def add_facility_operation():
    facility_id = input("시설 ID를 입력하세요: ")
    start_date = input("시작 날짜를 입력하세요 (YYYY-MM-DD 형식): ")
    end_date = input("종료 날짜를 입력하세요 (YYYY-MM-DD 형식): ")
    day_of_week = input("요일을 입력하세요: ")
    user_id = input("관리자 id를 입력하세요: ")

    try:
        cursor.execute("INSERT INTO FacilityOperation (facilityID, startDate, endDate, dayofWeek, userID) VALUES (%s, %s, %s, %s, %s)",
                       (facility_id, start_date, end_date, day_of_week, user_id))
        conn.commit()
        print("시설 운영 일정 추가 완료!")
    except psycopg2.Error as e:
        conn.rollback()
        print("시설 운영 일정 추가 중 오류 발생:", e)

# 시설 운영 일정 수정
def update_operation_schedule_from_input():
    schedule_id = input("수정할 일정의 ID를 입력하세요: ")
    new_start_date = input("새로운 시작 날짜를 입력하세요 (YYYY-MM-DD 형식): ")
    new_end_date = input("새로운 종료 날짜를 입력하세요 (YYYY-MM-DD 형식): ")
    new_day_of_week = input("새로운 요일을 입력하세요: ")
    new_user_id = input("새로운 관리자 id를 입력하세요: ")
    try:
        cursor.execute("SELECT * FROM FacilityOperation WHERE scheduleID = %s FOR UPDATE", (schedule_id,))
        # scheduleID에 해당하는 레코드를 잠금 설정

        cursor.execute("UPDATE FacilityOperation SET startDate = %s, endDate = %s, dayofWeek = %s, userID = %s WHERE scheduleID = %s",
                       (new_start_date, new_end_date, new_day_of_week, new_user_id, schedule_id))
        conn.commit()
        print("일정 수정 완료!")
    except psycopg2.Error as e:
        conn.rollback()
        print("일정 수정 중 오류 발생:", e)
    finally:
        cursor.execute("COMMIT")  # 커밋 또는 롤백을 위한 명시적인 커밋 명령어


# 시설 운영 일정 삭제
def delete_operation_schedule_by_input():
    schedule_ids = input("삭제할 일정의 ID를 입력하세요 (쉼표로 구분하여 여러 개 입력 가능): ").split(',')
    schedule_ids = [int(schedule_id.strip()) for schedule_id in schedule_ids if schedule_id.strip().isdigit()]

    try:
        if not schedule_ids:
            print("삭제할 일정의 유효한 ID를 입력하세요.")
            return

        cursor.execute("DELETE FROM FacilityOperation WHERE scheduleID IN %s", (tuple(schedule_ids),))
        conn.commit()

        if len(schedule_ids) == 1:
            print(f"일정 {schedule_ids[0]} 삭제 완료!")
        else:
            print(f"일정 {', '.join(str(sid) for sid in schedule_ids)} 삭제 완료!")
    except psycopg2.Error as e:
        conn.rollback()
        print("일정 삭제 중 오류 발생:", e)


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
                operation_info[2:] = ["-", "-", "-", "-"]  # 기본값으로 설정
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

    print("{:<5} {:<20} {:<20} {:<20} {:<20} {:<20} {:<20} {:<20}".format("ID", "이름", "유형", "위치", "시작일", "종료일", "요일", "관리자"))

    for facility in facilities:
        facility_id = facility[0]
        matching_operations = [op for op in operations if op[0] == facility_id]
        if matching_operations:
            for operation in matching_operations:
                start_date, end_date, day_of_week, user_id = operation[2], operation[3], operation[4], operation[5]
                print("{:<5} {:<20} {:<20} {:<20} {:<20} {:<20} {:<20} {:<20}".format(
                    facility[0], facility[1], facility[2], facility[3], start_date, end_date, day_of_week, user_id
                ))
        else:
            print("{:<5} {:<20} {:<20} {:<20} {:<20} {:<20} {:<20} {:<20}".format(
                facility[0], facility[1], facility[2], facility[3], "-", "-", "-", "-"
            ))
# 시설 평가 조회
def get_facility_reviews():
    try:
        facility_id = input("시설의 ID를 입력하세요: ")
        cursor.execute("SELECT * FROM FacilityReview WHERE facilityID = %s", (facility_id,))
        reviews = cursor.fetchall()

        if reviews:
            print("{:<5} {:<10} {:<10} {:<20}".format("ID", "Facility ID", "User ID", "Review"))
            for review in reviews:
                print("{:<5} {:<10} {:<10} {:<20}".format(review[0], review[1], review[2], review[4]))
        else:
            print("해당 시설에 대한 평가가 없습니다.")
    except psycopg2.Error as e:
        print("평가 조회 중 오류 발생:", e)

#시설 예약 조회
def check_reservations_for_facility():
    facility_id = input("시설 ID를 입력하세요: ")
    try:
        cursor.execute("""
            SELECT * FROM FacilityReservation WHERE facilityID = %s
        """, (facility_id,))
        reservations = cursor.fetchall()

        if reservations:
            print("시설 예약 내역:")
            for reservation in reservations:
                print(reservation)  # 예약 정보 출력
        else:
            print("해당 시설에 대한 예약이 없습니다.")
    except psycopg2.Error as e:
        print("예약 조회 중 오류 발생:", e)

###################################
def facility_menu():
    while True:
        print("메뉴")
        print("1. 시설 정보 조회")
        print("2. 시설 정보 수정")
        print("3. 시설 운영 일정 조회")
        print("4. 시설 운영 일정 수정")
        print("5. 시설 예약 조회")
        print("6. 시설 평가 조회")
        print("0. 종료")
        choice = input("번호를 입력하세요: ")

        if choice == "1":
            print_facility_information() #시설 정보 조회
        elif choice == "2":
            # 시설 정보 수정 함수 호출
            show_facility_update_menu()
            pass
        elif choice == "3":
            print_facility_information_with_operations()
        elif choice == "4":
            # 시설 운영 일정 수정 함수 호출
            show_facility_operation_menu()
            pass
        elif choice == "5":
            print_facility_information()
            check_reservations_for_facility()
        elif choice == "6":
            print_facility_information()
            get_facility_reviews()
        elif choice == "0":
            return
        else:
            print("잘못된 입력입니다. 다시 입력해주세요.")

def show_facility_update_menu():
    while True:
        print("메뉴")
        print("1. 시설 정보 추가")
        print("2. 시설 정보 변경")
        print("3. 시설 정보 삭제")
        print("0. 뒤로 가기")
        choice = input("번호를 입력하세요: ")

        if choice == "1":
            add_facility()
            facility_menu()
        elif choice == "2":
            print_facility_information()
            update_facility()
            facility_menu()
        elif choice == "3":
            # 시설 정보 삭제 함수 호출
            print_facility_information()
            delete_facility_by_id()
            facility_menu()
            pass
        elif choice == "0":
            break
        else:
            print("잘못된 입력입니다. 다시 입력해주세요.")

def show_facility_operation_menu():
    while True:
        print("메뉴")
        print("1. 시설 운영 일정 추가")
        print("2. 시설 운영 일정 변경")
        print("3. 시설 운영 일정 삭제")
        print("0. 뒤로 가기")
        choice = input("번호를 입력하세요: ")

        if choice == "1":
            # 시설 운영 일정 추가 함수 호출
            print_facility_information()
            add_facility_operation()
            print_facility_information_with_operations()
            facility_menu()
            pass
        elif choice == "2":
            # 시설 운영 일정 수정 함수 호출
            print_facility_information_with_operations()
            update_operation_schedule_from_input()
            facility_menu()
            pass
        elif choice == "3":
            # 시설 운영 일정 삭제 함수 호출
            print_facility_information_with_operations()
            delete_operation_schedule_by_input()
            facility_menu()
            pass
        elif choice == "0":
            #facility_menu()
            break
        else:
            print("잘못된 입력입니다. 다시 입력해주세요.")

# 변경사항 저장
conn.commit()

