import psycopg2
from schema import create_tables
from authentication import login_menu
from facility import facility_menu
from traffic import traffic_menu
from citizen import citizen_menu


# PostgreSQL 연결 설정
conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="#######",
    host="localhost",
    port="5432"
)
# 커서 생성
cursor = conn.cursor()

create_tables()

cursor.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON Facility TO FacilityManager;")
cursor.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON FacilityOperation TO FacilityManager;")
cursor.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON FacilityReview TO Citizen;")
cursor.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON TrafficInformation TO TrafficManager;")
######################

userID, role = login_menu()
if role == 'FacilityManager':
    facility_menu()
elif role == 'TrafficManager':
    traffic_menu()
elif role == 'Citizen':
    citizen_menu()
######################

# 변경사항 저장
conn.commit()

conn.close()