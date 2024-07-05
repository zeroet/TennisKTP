import pandas as pd
import streamlit as st
import base64

# 초기 유저 데이터프레임 생성
def initialize_users():
    df = pd.DataFrame(columns=['Player', 'Ranking Points', 'Wins', 'Losses', 'Draws', 'Championships', 'Guest'])
    return df

# 점수 계산 함수 (Elo 시스템 기반, 정수 점수)
def calculate_elo(winner_rp, loser_rp):
    k = 32
    expected_winner = 1 / (1 + 10 ** ((loser_rp - winner_rp) / 400))
    expected_loser = 1 / (1 + 10 ** ((winner_rp - loser_rp) / 400))

    winner_new_rp = int(winner_rp + k * (1 - expected_winner))
    loser_new_rp = int(loser_rp + k * (0 - expected_loser))

    return winner_new_rp, loser_new_rp

# 유저 점수 업데이트 함수
def update_scores(df, winner, loser):
    winner_index = df[df['Player'] == winner].index[0]
    loser_index = df[df['Player'] == loser].index[0]

    df.at[winner_index, 'Wins'] += 1
    df.at[loser_index, 'Losses'] += 1

    new_rp_winner, new_rp_loser = calculate_elo(df.at[winner_index, 'Ranking Points'], df.at[loser_index, 'Ranking Points'])
    
    df.at[winner_index, 'Ranking Points'] = new_rp_winner
    df.at[loser_index, 'Ranking Points'] = new_rp_loser

    return df

# 엑셀 파일로 저장
def save_to_excel(df, filename='league_of_ktp.xlsx'):
    df.to_excel(filename, index=False)

# 엑셀 파일에서 데이터 불러오기
def load_from_excel(filename='league_of_ktp.xlsx'):
    try:
        df = pd.read_excel(filename)
        # 'Guest' 열이 없는 경우 기본값으로 False를 추가
        if 'Guest' not in df.columns:
            df['Guest'] = False
    except FileNotFoundError:
        df = initialize_users()
    return df

# 이미지 파일을 base64로 인코딩하는 함수
def b64_image(filename):
    with open(filename, "rb") as f:
        return base64.b64encode(f.read()).decode()

# 왕관 아이콘 추가 함수
def add_crown_icons(ranking_df):
    gold_crown = f'<img src="data:image/png;base64,{b64_image("gold_crown.png")}" width="16" height="16"/>'
    silver_crown = f'<img src="data:image/png;base64,{b64_image("silver_crown.png")}" width="16" height="16"/>'
    bronze_crown = f'<img src="data:image/png;base64,{b64_image("bronze_crown.png")}" width="16" height="16"/>'
    
    if len(ranking_df) > 0:
        ranking_df.at[0, 'Player'] += f' {gold_crown}'
    if len(ranking_df) > 1:
        ranking_df.at[1, 'Player'] += f' {silver_crown}'
    if len(ranking_df) > 2:
        ranking_df.at[2, 'Player'] += f' {bronze_crown}'
    
    return ranking_df

# HTML로 데이터프레임 표시 함수
def render_html_table(df):
    html = df.to_html(escape=False, index=False)
    return html

# Streamlit 애플리케이션
# tennis_ball = f'<img src="data:image/png;base64,{b64_image("tennis.png")}" width="16" height="16"/>'
st.set_page_config(layout="wide")  # 페이지 레이아웃을 넓게 설정
st.title('League of KTP')

df = load_from_excel()

st.header('Player Rankings')
# 랭킹과 게스트 유저 구분
ranking_df = df[df['Guest'] == False].sort_values(by='Ranking Points', ascending=False).reset_index(drop=True)
ranking_df = add_crown_icons(ranking_df)
ranking_df.index = ranking_df.index + 1  # 인덱스를 1부터 시작
ranking_df.index.name = 'Rank'
guest_df = df[df['Guest'] == True].sort_values(by='Player').reset_index(drop=True)
guest_df.index = ['G' + str(i+1) for i in range(len(guest_df))]  # 게스트 인덱스에 G 추가
combined_df = pd.concat([ranking_df, guest_df]).reset_index()

# HTML로 테이블 렌더링
html_table = render_html_table(combined_df[['index', 'Player', 'Ranking Points', 'Wins', 'Losses', 'Draws', 'Championships']])
st.markdown(html_table, unsafe_allow_html=True)

st.header('Record a Match Result')
col1, col2, col3 = st.columns(3)

with col1:
    player1 = st.selectbox('Player 1', df['Player'])
with col2:
    player2 = st.selectbox('Player 2', df['Player'])
with col3:
    result = st.selectbox('Winner', ['player1', 'player2', 'draw'])

if st.button('Submit Result'):
    if player1 != player2:
        if result == 'player1':
            df = update_scores(df, player1, player2)
        elif result == 'player2':
            df = update_scores(df, player2, player1)
        save_to_excel(df)
        df = load_from_excel()  # 데이터 재로드하여 테이블 업데이트
        ranking_df = df[df['Guest'] == False].sort_values(by='Ranking Points', ascending=False).reset_index(drop=True)
        ranking_df = add_crown_icons(ranking_df)
        ranking_df.index = ranking_df.index + 1  # 인덱스를 1부터 시작
        ranking_df.index.name = 'Rank'
        guest_df = df[df['Guest'] == True].sort_values(by='Player').reset_index(drop=True)
        guest_df.index = ['G' + str(i+1) for i in range(len(guest_df))]  # 게스트 인덱스에 G 추가
        combined_df = pd.concat([ranking_df, guest_df]).reset_index()
        html_table = render_html_table(combined_df[['index', 'Player', 'Ranking Points', 'Wins', 'Losses', 'Draws', 'Championships']])
        st.markdown(html_table, unsafe_allow_html=True)
        st.success(f'{player1} vs {player2} 경기 결과 기록 완료.')
    else:
        st.error('두 플레이어는 동일할 수 없습니다.')

st.header('Add New Player')
new_player = st.text_input('Player Name')

if st.button('Add Player'):
    if new_player and new_player not in df['Player'].values:
        new_data = pd.DataFrame([[new_player, 1000, 0, 0, 0, 0, False]], columns=['Player', 'Ranking Points', 'Wins', 'Losses', 'Draws', 'Championships', 'Guest'])
        df = pd.concat([df, new_data], ignore_index=True)
        save_to_excel(df)
        df = load_from_excel()  # 데이터 재로드하여 테이블 업데이트
        ranking_df = df[df['Guest'] == False].sort_values(by='Ranking Points', ascending=False).reset_index(drop=True)
        ranking_df = add_crown_icons(ranking_df)
        ranking_df.index = ranking_df.index + 1  # 인덱스를 1부터 시작
        ranking_df.index.name = 'Rank'
        guest_df = df[df['Guest'] == True].sort_values(by='Player').reset_index(drop=True)
        guest_df.index = ['G' + str(i+1) for i in range(len(guest_df))]  # 게스트 인덱스에 G 추가
        combined_df = pd.concat([ranking_df, guest_df]).reset_index()
        html_table = render_html_table(combined_df[['index', 'Player', 'Ranking Points', 'Wins', 'Losses', 'Draws', 'Championships']])
        st.markdown(html_table, unsafe_allow_html=True)
        st.success(f'플레이어 {new_player} 추가 완료.')
    else:
        st.error('플레이어 이름을 입력하거나 이미 존재하는 플레이어입니다.')

st.header('Record a Championship Win')
champion = st.selectbox('Champion', df['Player'])

if st.button('Submit Championship Win'):
    champ_index = df[df['Player'] == champion].index[0]
    df.at[champ_index, 'Championships'] += 1
    df.at[champ_index, 'Ranking Points'] += 50  # 챔피언십 포인트 추가
    save_to_excel(df)
    df = load_from_excel()  # 데이터 재로드하여 테이블 업데이트
    ranking_df = df[df['Guest'] == False].sort_values(by='Ranking Points', ascending=False).reset_index(drop=True)
    ranking_df = add_crown_icons(ranking_df)
    ranking_df.index = ranking_df.index + 1  # 인덱스를 1부터 시작
    ranking_df.index.name = 'Rank'
    guest_df = df[df['Guest'] == True].sort_values(by='Player').reset_index(drop=True)
    guest_df.index = ['G' + str(i+1) for i in range(len(guest_df))]  # 게스트 인덱스에 G 추가
    combined_df = pd.concat([ranking_df, guest_df]).reset_index()
    html_table = render_html_table(combined_df[['index', 'Player', 'Ranking Points', 'Wins', 'Losses', 'Draws', 'Championships']])
    st.markdown(html_table, unsafe_allow_html=True)
    st.success(f'{champion}의 우승 횟수가 추가되고 100 랭킹 포인트가 추가되었습니다.')

st.header('Add Guest Player')
new_guest = st.text_input('Guest Player Name')

if st.button('Add Guest Player'):
    if new_guest and new_guest not in df['Player'].values:
        new_data = pd.DataFrame([[new_guest, 1000, 0, 0, 0, 0, True]], columns=['Player', 'Ranking Points', 'Wins', 'Losses', 'Draws', 'Championships', 'Guest'])
        df = pd.concat([df, new_data], ignore_index=True)
        save_to_excel(df)
        df = load_from_excel()  # 데이터 재로드하여 테이블 업데이트
        ranking_df = df[df['Guest'] == False].sort_values(by='Ranking Points', ascending=False).reset_index(drop=True)
        ranking_df = add_crown_icons(ranking_df)
        ranking_df.index = ranking_df.index + 1  # 인덱스를 1부터 시작
        ranking_df.index.name = 'Rank'
        guest_df = df[df['Guest'] == True].sort_values(by='Player').reset_index(drop=True)
        guest_df.index = ['G' + str(i+1) for i in range(len(guest_df))]  # 게스트 인덱스에 G 추가
        combined_df = pd.concat([ranking_df, guest_df]).reset_index()
        html_table = render_html_table(combined_df[['index', 'Player', 'Ranking Points', 'Wins', 'Losses', 'Draws', 'Championships']])
        st.markdown(html_table, unsafe_allow_html=True)
        st.success(f'게스트 플레이어 {new_guest} 추가 완료.')
    else:
        st.error('플레이어 이름을 입력하거나 이미 존재하는 플레이어입니다.')

st.header('Delete Guest Player')
guest_to_delete = st.selectbox('Select Guest Player to Delete', df[df['Guest'] == True]['Player'])

if st.button('Delete Guest Player'):
    if guest_to_delete:
        df = df[df['Player'] != guest_to_delete]
        save_to_excel(df)
        df = load_from_excel()  # 데이터 재로드하여 테이블 업데이트
        ranking_df = df[df['Guest'] == False].sort_values(by='Ranking Points', ascending=False).reset_index(drop=True)
        ranking_df = add_crown_icons(ranking_df)
        ranking_df.index = ranking_df.index + 1  # 인덱스를 1부터 시작
        ranking_df.index.name = 'Rank'
        guest_df = df[df['Guest'] == True].sort_values(by='Player').reset_index(drop=True)
        guest_df.index = ['G' + str(i+1) for i in range(len(guest_df))]  # 게스트 인덱스에 G 추가
        combined_df = pd.concat([ranking_df, guest_df]).reset_index()
        html_table = render_html_table(combined_df[['index', 'Player', 'Ranking Points', 'Wins', 'Losses', 'Draws', 'Championships']])
        st.markdown(html_table, unsafe_allow_html=True)
        st.success(f'게스트 플레이어 {guest_to_delete} 삭제 완료.')
    else:
        st.error('게스트 플레이어를 선택하세요.')
