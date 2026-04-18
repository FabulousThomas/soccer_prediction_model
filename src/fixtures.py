import pandas as pd
import requests
import io

def get_upcoming_fixtures():
    # URL for football-data.co.uk weekly fixtures
    url = "https://www.football-data.co.uk/fixtures.csv"
    
    print("📡 Fetching upcoming fixtures...")
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print("❌ Could not fetch fixtures.")
        return []

    # Load into pandas
    df = pd.read_csv(io.StringIO(response.text))
    
    # Fix encoding issue with division column
    df.columns = df.columns.str.replace('ï»¿', '', regex=True)
    
        
    # Filter for all available leagues - include European and other major leagues
    target_divisions = [
        'E0',  # Premier League
        'D1',  # Bundesliga  
        'SP1',  # La Liga
        'I1',  # Serie A
        'F1',  # Ligue 1
        'SC0', # Scottish Premiership
        'SC1', # Scottish Championship
        'E1',  # Championship
        'E2',  # League One
        'E3',  # League Two
        'N1',  # Eredivisie (Dutch)
        'B1',  # Belgian Pro League
        'P1',  # Primeira Liga (Portugal)
        'T1',  # Turkish Super Lig
        'G1',  # Greek Super League
        'D2', # 2. Bundesliga
        'D3', # 3. Liga
    ]
    
    if 'Div' in df.columns:
        filtered_df = df[df['Div'].isin(target_divisions)]
        fixtures = list(zip(filtered_df['HomeTeam'], filtered_df['AwayTeam']))
        print(f"✅ Found {len(fixtures)} upcoming matches from all available leagues.")
    else:
        # If no Div column, use all fixtures
        fixtures = list(zip(df['HomeTeam'], df['AwayTeam']))
        print(f"✅ Found {len(fixtures)} upcoming matches (all leagues).")
    return fixtures