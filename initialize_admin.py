import pandas as pd
import hashlib

# 초기 사용자 데이터프레임 생성
def initialize_users():
    df = pd.DataFrame(columns=['UserID', 'Password', 'Username', 'Role', 'Approved'])
    return df

# 비밀번호 해싱 함수
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# 초기 엑셀 파일 생성
def initialize_excel(filename='users.xlsx'):
    df = initialize_users()
    # 초기 admin 유저 추가
    admin_user = pd.DataFrame([{
        'UserID': 'admin',
        'Password': hash_password('admin_password'),  # 초기 admin 비밀번호를 설정합니다.
        'Username': 'Admin User',
        'Role': 'admin',
        'Approved': True
    }])
    df = pd.concat([df, admin_user], ignore_index=True)
    df.to_excel(filename, index=False)

# 엑셀 파일 초기화 실행
initialize_excel()
