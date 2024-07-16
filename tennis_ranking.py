import pandas as pd
import streamlit as st
import base64
import os

def tennis_ranking_page():
    def initialize_users():
        df = pd.DataFrame(columns=['Player', 'Ranking Points', 'Wins', 'Losses', 'Draws', 'Championships', 'Guest'])
        return df

    def calculate_elo(winner_rp, loser_rp):
        k = 32
        expected_winner = 1 / (1 + 10 ** ((loser_rp - winner_rp) / 400))
        expected_loser = 1 / (1 + 10 ** ((winner_rp - loser_rp) / 400))

        winner_new_rp = int(winner_rp + k * (1 - expected_winner))
        loser_new_rp = int(loser_rp + k * (0 - expected_loser))

        return winner_new_rp, loser_new_rp

    def calculate_double_elo(winner_rps, loser_rps):
        k = 32
        avg_winner_rp = sum(winner_rps) / 2
        avg_loser_rp = sum(loser_rps) / 2

        expected_winner = 1 / (1 + 10 ** ((avg_loser_rp - avg_winner_rp) / 400))
        expected_loser = 1 / (1 + 10 ** ((avg_winner_rp - avg_loser_rp) / 400))

        winner_new_rps = [int(rp + k * (1 - expected_winner)) for rp in winner_rps]
        loser_new_rps = [int(rp + k * (0 - expected_loser)) for rp in loser_rps]

        return winner_new_rps, loser_new_rps

    def update_scores(df, winner, loser):
        winner_index = df[df['Player'] == winner].index[0]
        loser_index = df[df['Player'] == loser].index[0]

        df.at[winner_index, 'Wins'] += 1
        df.at[loser_index, 'Losses'] += 1

        new_rp_winner, new_rp_loser = calculate_elo(df.at[winner_index, 'Ranking Points'], df.at[loser_index, 'Ranking Points'])

        df.at[winner_index, 'Ranking Points'] = new_rp_winner
        df.at[loser_index, 'Ranking Points'] = new_rp_loser

        return df

    def update_double_scores(df, winner_team, loser_team):
        winner_indices = [df[df['Player'] == player].index[0] for player in winner_team]
        loser_indices = [df[df['Player'] == player].index[0] for player in loser_team]

        for idx in winner_indices:
            df.at[idx, 'Wins'] += 1
        for idx in loser_indices:
            df.at[idx, 'Losses'] += 1

        winner_rps = [df.at[idx, 'Ranking Points'] for idx in winner_indices]
        loser_rps = [df.at[idx, 'Ranking Points'] for idx in loser_indices]

        new_winner_rps, new_loser_rps = calculate_double_elo(winner_rps, loser_rps)

        for idx, new_rp in zip(winner_indices, new_winner_rps):
            df.at[idx, 'Ranking Points'] = new_rp
        for idx, new_rp in zip(loser_indices, new_loser_rps):
            df.at[idx, 'Ranking Points'] = new_rp

        return df

    def save_to_excel(df, filename='league_of_ktp.xlsx'):
        df.to_excel(filename, index=False)

    def load_from_excel(filename='league_of_ktp.xlsx'):
        try:
            df = pd.read_excel(filename)
            if 'Guest' not in df.columns:
                df['Guest'] = False
        except FileNotFoundError:
            df = initialize_users()
        return df

    def b64_image(filename):
        with open(filename, "rb") as f:
            return base64.b64encode(f.read()).decode()

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

    def render_html_table(df):
        df.rename(columns={'index': 'Rank'}, inplace=True)
        html = df.to_html(escape=False, index=False)
        return html

    st.title('League of KTP')

    df = load_from_excel()

    st.header('Player Rankings')
    ranking_df = df[df['Guest'] == False].sort_values(by='Ranking Points', ascending=False).reset_index(drop=True)
    ranking_df = add_crown_icons(ranking_df)
    ranking_df.index = ranking_df.index + 1
    ranking_df.index.name = 'Rank'
    guest_df = df[df['Guest'] == True].sort_values(by='Player').reset_index(drop=True)
    guest_df.index = ['G' + str(i+1) for i in range(len(guest_df))]
    combined_df = pd.concat([ranking_df, guest_df]).reset_index()
    combined_df.rename(columns={'index': 'Rank'}, inplace=True)
    html_table = render_html_table(combined_df[['Rank', 'Player', 'Ranking Points', 'Wins', 'Losses', 'Draws', 'Championships']])
    st.markdown(html_table, unsafe_allow_html=True)

    st.header('Next Match')
    screenshots = sorted(os.listdir("screenshots"), reverse=True)
    if screenshots:
        st.image(f"screenshots/{screenshots[0]}", use_column_width='auto')

    if st.session_state.role == 'admin':
        st.header('Record a Match Result')
        match_type = st.radio('Match Type', ['Single', 'Double'])

        if match_type == 'Single':
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
                    df = load_from_excel()
                    ranking_df = df[df['Guest'] == False].sort_values(by='Ranking Points', ascending=False).reset_index(drop=True)
                    ranking_df = add_crown_icons(ranking_df)
                    ranking_df.index = ranking_df.index + 1
                    ranking_df.index.name = 'Rank'
                    guest_df = df[df['Guest'] == True].sort_values(by='Player').reset_index(drop=True)
                    guest_df.index = ['G' + str(i+1) for i in range(len(guest_df))]
                    combined_df = pd.concat([ranking_df, guest_df]).reset_index()
                    combined_df.rename(columns={'index': 'Rank'}, inplace=True)
                    html_table = render_html_table(combined_df[['Rank', 'Player', 'Ranking Points', 'Wins', 'Losses', 'Draws', 'Championships']])
                    st.markdown(html_table, unsafe_allow_html=True)
                    st.success(f'{player1} vs {player2} 경기 결과 기록 완료.')
                else:
                    st.error('두 플레이어는 동일할 수 없습니다.')
        
        elif match_type == 'Double':
            col1, col2 = st.columns(2)
            with col1:
                team_a_player1 = st.selectbox('Team A - Player 1', df['Player'])
                team_a_player2 = st.selectbox('Team A - Player 2', df['Player'])
            with col2:
                team_b_player1 = st.selectbox('Team B - Player 1', df['Player'])
                team_b_player2 = st.selectbox('Team B - Player 2', df['Player'])
            
            result = st.selectbox('Winner', ['Team A', 'Team B', 'Draw'])
            
            if st.button('Submit Double Result'):
                if len(set([team_a_player1, team_a_player2, team_b_player1, team_b_player2])) == 4:
                    if result == 'Team A':
                        df = update_double_scores(df, [team_a_player1, team_a_player2], [team_b_player1, team_b_player2])
                    elif result == 'Team B':
                        df = update_double_scores(df, [team_b_player1, team_b_player2], [team_a_player1, team_a_player2])
                    save_to_excel(df)
                    df = load_from_excel()
                    ranking_df = df[df['Guest'] == False].sort_values(by='Ranking Points', ascending=False).reset_index(drop=True)
                    ranking_df = add_crown_icons(ranking_df)
                    ranking_df.index = ranking_df.index + 1
                    ranking_df.index.name = 'Rank'
                    guest_df = df[df['Guest'] == True].sort_values(by='Player').reset_index(drop=True)
                    guest_df.index = ['G' + str(i+1) for i in range(len(guest_df))]
                    combined_df = pd.concat([ranking_df, guest_df]).reset_index()
                    combined_df.rename(columns={'index': 'Rank'}, inplace=True)
                    html_table = render_html_table(combined_df[['Rank', 'Player', 'Ranking Points', 'Wins', 'Losses', 'Draws', 'Championships']])
                    st.markdown(html_table, unsafe_allow_html=True)
                    st.success('Double match result recorded successfully.')
                else:
                    st.error('Each player should be unique in a double match.')

        st.header('Add New Player')
        new_player = st.text_input('Player Name')

        if st.button('Add Player'):
            if new_player and new_player not in df['Player'].values:
                new_data = pd.DataFrame([[new_player, 1000, 0, 0, 0, 0, False]], columns=['Player', 'Ranking Points', 'Wins', 'Losses', 'Draws', 'Championships', 'Guest'])
                df = pd.concat([df, new_data], ignore_index=True)
                save_to_excel(df)
                df = load_from_excel()
                ranking_df = df[df['Guest'] == False].sort_values(by='Ranking Points', ascending=False).reset_index(drop=True)
                ranking_df = add_crown_icons(ranking_df)
                ranking_df.index = ranking_df.index + 1
                ranking_df.index.name = 'Rank'
                guest_df = df[df['Guest'] == True].sort_values(by='Player').reset_index(drop=True)
                guest_df.index = ['G' + str(i+1) for i in range(len(guest_df))]
                combined_df = pd.concat([ranking_df, guest_df]).reset_index()
                combined_df.rename(columns={'index': 'Rank'}, inplace=True)
                html_table = render_html_table(combined_df[['Rank', 'Player', 'Ranking Points', 'Wins', 'Losses', 'Draws', 'Championships']])
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
            df = load_from_excel()
            ranking_df = df[df['Guest'] == False].sort_values(by='Ranking Points', ascending=False).reset_index(drop=True)
            ranking_df = add_crown_icons(ranking_df)
            ranking_df.index = ranking_df.index + 1
            ranking_df.index.name = 'Rank'
            guest_df = df[df['Guest'] == True].sort_values(by='Player').reset_index(drop=True)
            guest_df.index = ['G' + str(i+1) for i in range(len(guest_df))]
            combined_df = pd.concat([ranking_df, guest_df]).reset_index()
            combined_df.rename(columns={'index': 'Rank'}, inplace=True)
            html_table = render_html_table(combined_df[['Rank', 'Player', 'Ranking Points', 'Wins', 'Losses', 'Draws', 'Championships']])
            st.markdown(html_table, unsafe_allow_html=True)
            st.success(f'{champion}의 우승 횟수가 추가되고 100 랭킹 포인트가 추가되었습니다.')

        st.header('Add Guest Player')
        new_guest = st.text_input('Guest Player Name')

        if st.button('Add Guest Player'):
            if new_guest and new_guest not in df['Player'].values:
                new_data = pd.DataFrame([[new_guest, 1000, 0, 0, 0, 0, True]], columns=['Player', 'Ranking Points', 'Wins', 'Losses', 'Draws', 'Championships', 'Guest'])
                df = pd.concat([df, new_data], ignore_index=True)
                save_to_excel(df)
                df = load_from_excel()
                ranking_df = df[df['Guest'] == False].sort_values(by='Ranking Points', ascending=False).reset_index(drop=True)
                ranking_df = add_crown_icons(ranking_df)
                ranking_df.index = ranking_df.index + 1
                ranking_df.index.name = 'Rank'
                guest_df = df[df['Guest'] == True].sort_values(by='Player').reset_index(drop=True)
                guest_df.index = ['G' + str(i+1) for i in range(len(guest_df))]
                combined_df = pd.concat([ranking_df, guest_df]).reset_index()
                combined_df.rename(columns={'index': 'Rank'}, inplace=True)
                html_table = render_html_table(combined_df[['Rank', 'Player', 'Ranking Points', 'Wins', 'Losses', 'Draws', 'Championships']])
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
                df = load_from_excel()
                ranking_df = df[df['Guest'] == False].sort_values(by='Ranking Points', ascending=False).reset_index(drop=True)
                ranking_df = add_crown_icons(ranking_df)
                ranking_df.index = ranking_df.index + 1
                ranking_df.index.name = 'Rank'
                guest_df = df[df['Guest'] == True].sort_values(by='Player').reset_index(drop=True)
                guest_df.index = ['G' + str(i+1) for i in range(len(guest_df))]
                combined_df = pd.concat([ranking_df, guest_df]).reset_index()
                combined_df.rename(columns={'index': 'Rank'}, inplace=True)
                html_table = render_html_table(combined_df[['Rank', 'Player', 'Ranking Points', 'Wins', 'Losses', 'Draws', 'Championships']])
                st.markdown(html_table, unsafe_allow_html=True)
                st.success(f'게스트 플레이어 {guest_to_delete} 삭제 완료.')
            else:
                st.error('게스트 플레이어를 선택하세요.')
    else:
        st.header('Player Rankings')
        html_table = render_html_table(ranking_df[['Rank', 'Player', 'Ranking Points']])
        st.markdown(html_table, unsafe_allow_html=True)
        st.header('Next Match')
        if screenshots:
            st.image(f"screenshots/{screenshots[0]}", use_column_width='auto')
