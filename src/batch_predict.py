from src.predict import SoccerPredictor
from src.notify import send_alert
from datetime import datetime
import pandas as pd
import requests
import io

def get_fixtures_with_divisions():
    """Get fixtures with division information for sorting"""
    url = "https://www.football-data.co.uk/fixtures.csv"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print("❌ Could not fetch fixtures.")
        return []
    
    df = pd.read_csv(io.StringIO(response.text))
    df.columns = df.columns.str.replace('ï»¿', '', regex=True)
    
    return df

def run_weekend_analysis(fixtures):
    """
    fixtures: List of tuples [("HomeTeam", "AwayTeam"), ...]
    """
    predictor = SoccerPredictor()
    results = []

    # Get fixtures with division info
    fixtures_df = get_fixtures_with_divisions()
    
    # Add division info to fixtures
    fixtures_with_div = []
    for home, away in fixtures:
        # Find the division for this fixture
        match_row = fixtures_df[(fixtures_df['HomeTeam'] == home) & (fixtures_df['AwayTeam'] == away)]
        if not match_row.empty:
            div = match_row['Div'].iloc[0] if 'Div' in match_row.columns else 'Unknown'
            fixtures_with_div.append((home, away, div))
        else:
            fixtures_with_div.append((home, away, 'Unknown'))

    print(f"\n⚽ AI PREDICTIONS FOR THE WEEKEND (April 18-19, 2026) - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 95)
    print(f"{'Matchup':<35} | {'League':<8} | {'Win %':<10} | {'Draw %':<8} | {'Away %':<8} | {'O1.5%':<8} | {'O2.5%':<8} | {'Corners':<8}")
    print("-" * 95)

    # Sort by division
    league_names = {
        'E0': 'Premier League',
        'D1': 'Bundesliga',
        'SP1': 'La Liga', 
        'I1': 'Serie A',
        'F1': 'Ligue 1',
        'E1': 'Championship',
        'E2': 'League One',
        'E3': 'League Two',
        'N1': 'Eredivisie',
        'B1': 'Belgian Pro League',
        'P1': 'Primeira Liga',
        'T1': 'Turkish Super Lig',
        'G1': 'Greek Super League',
        'D2': '2. Bundesliga',
        'D3': '3. Liga',
        'SC0': 'Scottish Premiership',
        'SC1': 'Scottish Championship'
    }

    # Save predictions to CSV file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"predictions_{timestamp}.csv"
    
    # Create CSV data
    csv_data = []
    csv_data.append(['Matchup', 'League', 'Home Win %', 'Draw %', 'Away Win %', 'O1.5 %', 'O2.5 %', 'Expected Corners', 'Hot Pick'])
    
    for home, away, div in sorted(fixtures_with_div, key=lambda x: x[2]):
        try:
            res = predictor.predict_match(home, away)
            
            match_name = f"{home} vs {away}"
            win_prob = f"{res['probabilities']['Home']:.1%}"
            draw_prob = f"{res['draw_prob']:.1%}"
            away_prob = f"{res['away_win_prob']:.1%}"
            o15_prob = f"{res['over_1_5_prob']:.1%}"
            o25_prob = f"{res['over_2_5_prob']:.1%}"
            total_corners = f"{res['exp_corners']['Home'] + res['exp_corners']['Away']:.1f}"
            marker = "🔥" if res['over_2_5_prob'] > 0.6 else ""
            
            league_name = league_names.get(div, div)
            
            csv_data.append([match_name, league_name, win_prob, draw_prob, away_prob, o15_prob, o25_prob, total_corners, marker])
            
            # Format the output
            win_prob = f"{res['probabilities']['Home']:.0%}"
            draw_prob = f"{res['draw_prob']:.0%}"
            away_prob = f"{res['away_win_prob']:.0%}"
            o15_prob = f"{res['over_1_5_prob']:.0%}"
            o25_prob = f"{res['over_2_5_prob']:.0%}"
            total_corners = f"{res['exp_corners']['Home'] + res['exp_corners']['Away']:.1f}"
            
            # Highlight high-probability games (e.g., > 60% Over 2.5)
            marker = "🔥" if res['over_2_5_prob'] > 0.6 else "  "
            
            print(f"{match_name:<35} | {league_name:<8} | {win_prob:<10} | {draw_prob:<8} | {away_prob:<8} | {o15_prob:<8} | {o25_prob:<8} | {total_corners:<8} {marker}")
            
            results.append(res)
        except KeyError:
            print(f"⚠️  Skipping {home} vs {away} (Team name mismatch)")

    # Write to CSV
    df = pd.DataFrame(csv_data[1:], columns=csv_data[0])
    df.to_csv(f"data/predictions/{filename}", index=False, encoding='utf-8')
    
    print(f"✅ Predictions saved to data/predictions/{filename}")
    return results

def send_summary_to_telegram(results):
    msg = "⚽ *Weekend AI Preview* ⚽\n\n"
    
    # We'll pick the top 5 games by Over 2.5 Probability
    top_picks = sorted(results, key=lambda x: x['over_2_5_prob'], reverse=True)[:5]
    
    for res in top_picks:
        match = res['teams']
        o25 = res['over_2_5_prob']
        h_win = res['probabilities']['Home']
        
        msg += f"🏟 *{match}*\n"
        msg += f"📈 O2.5 Prob: {o25:.1%}\n"
        msg += f"🏠 Home Win: {h_win:.1%}\n"
        msg += "--------------------------\n"

    send_alert(msg)

if __name__ == "__main__":
    # EXAMPLE FIXTURES (Ensure names match your CSV files!)
    upcoming_games = [
        ("Arsenal", "Man United"),
        ("Real Madrid", "Barcelona"),
        ("Bayern Munich", "Dortmund"),
        ("Liverpool", "Man City"),
        ("Inter", "Milan"),
        ("PSG", "Lyon")
    ]
    
    run_weekend_analysis(upcoming_games)