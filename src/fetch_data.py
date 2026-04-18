import os, requests, kagglehub, pandas as pd

def download_data():
    # Seasons 23/24, 24/25, and current 25/26
    seasons, main_leagues = ['2324', '2425', '2526'], ['E0', 'E1', 'D1', 'SP1', 'I1', 'F1']
    all_data = []
    print("Fetching Domestic Data...")
    for s in seasons:
        for l in main_leagues:
            try:
                url = f"https://www.football-data.co.uk/mmz4281/{s}/{l}.csv"
                # HC/AC are corners; FTHG/FTAG are goals
                df = pd.read_csv(url, usecols=['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'HC', 'AC'])
                df = df.dropna()
                all_data.append(df)
            except: continue
    pd.concat(all_data).to_csv('data/raw/expanded_leagues.csv', index=False)

    print("Fetching International Data...")
    path = kagglehub.dataset_download("martj42/international-football-results-from-1872-to-2017")
    df_intl = pd.read_csv(os.path.join(path, "results.csv"))
    df_intl['date'] = pd.to_datetime(df_intl['date'])
    # Filter for recency to keep EC2 memory usage low
    df_intl[df_intl['date'] >= '2023-01-01'].to_csv('data/raw/intl_results.csv', index=False)

if __name__ == "__main__":
    download_data()