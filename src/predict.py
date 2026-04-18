import os
import pickle
import numpy as np
from scipy.stats import poisson
from dotenv import load_dotenv

load_dotenv()

class SoccerPredictor:
    def __init__(self):
        model_path = os.getenv("MODEL_PATH", "models/soccer_master.pkl")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at {model_path}. Run training first.")
        
        with open(model_path, 'rb') as f:
            data = pickle.load(f)
            self.model = data['model']
            self.elos = data['elos']
            self.corners = data['corners']

    def predict_match(self, home_team, away_team):
        # 1. Get current stats or defaults for new teams
        h_elo = self.elos.get(home_team, 1500)
        a_elo = self.elos.get(away_team, 1500)
        h_style = self.corners.get(home_team, 5.0)
        a_style = self.corners.get(away_team, 5.0)

        # 2. Model Inference: [H_Goals, A_Goals, H_Corners, A_Corners]
        features = np.array([[h_elo, a_elo, h_elo - a_elo, h_style, a_style]], dtype=np.float32)
        preds = self.model.predict(features)[0]
        
        # Ensure we don't have negative predictions
        h_g_avg, a_g_avg = max(0.1, preds[0]), max(0.1, preds[1])
        h_c_avg, a_c_avg = max(0.0, preds[2]), max(0.0, preds[3])

        # 3. Probability Matrix (Poisson)
        p_h, p_d, p_a = 0, 0, 0
        p_over_1_5, p_over_2_5 = 0, 0
        
        for h in range(7): # Check up to 6 goals
            for a in range(7):
                prob = poisson.pmf(h, h_g_avg) * poisson.pmf(a, a_g_avg)
                
                # Win/Draw/Away logic
                if h > a: p_h += prob
                elif h == a: p_d += prob
                else: p_a += prob
                
                # Goal Over/Under logic
                if (h + a) > 1.5: p_over_1_5 += prob
                if (h + a) > 2.5: p_over_2_5 += prob

        return {
            "teams": f"{home_team} vs {away_team}",
            "probabilities": {"Home": p_h, "Draw": p_d, "Away": p_a},
            "exp_goals": {"Home": h_g_avg, "Away": a_g_avg},
            "exp_corners": {"Home": h_c_avg, "Away": a_c_avg},
            "total_goals_avg": h_g_avg + a_g_avg,
            "goals": {"O1.5": p_over_1_5, "O2.5": p_over_2_5},
            "over_1_5_prob": p_over_1_5,
            "over_2_5_prob": p_over_2_5,
            "draw_prob": p_d,
            "away_win_prob": p_a
        }

if __name__ == "__main__":
    # Test call
    import sys
    if len(sys.argv) > 2:
        predictor = SoccerPredictor()
        res = predictor.predict_match(sys.argv[1], sys.argv[2])
        
        print(f"\n--- {res['teams']} ---")
        print(f"Probabilities: H: {res['probabilities']['Home']:.1%} | D: {res['probabilities']['Draw']:.1%} | A: {res['probabilities']['Away']:.1%}")
        print(f"Exp. Goals: {res['exp_goals']['Home']:.2f} - {res['exp_goals']['Away']:.2f}")
        print(f"Exp. Corners: {res['exp_corners']['Home']:.2f} - {res['exp_corners']['Away']:.2f}")
        print(f"Over 2.5 Goals: {res['over_2_5_prob']:.1%}")
    else:
        print("Usage: python3 predictor.py 'Home Team' 'Away Team'")