import os
import pandas as pd
import numpy as np
import xgboost as xgb
import pickle
from sklearn.multioutput import MultiOutputRegressor
from dotenv import load_dotenv

load_dotenv()

def train_model():
    # Relative path from the project root
    df = pd.read_csv(os.getenv("DATA_PATH"))
    # Handle European date format (DD/MM/YYYY)
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Date'])  # Remove rows with broken dates
    # df = df.sort_values('Date').dropna()

    # Elo & Corner Logic
    elo = {t: 1500 for t in pd.concat([df['HomeTeam'], df['AwayTeam']]).unique()}
    corners = {t: 5.0 for t in elo.keys()}
    
    features, targets = [], []
    for _, row in df.iterrows():
        h, a = row['HomeTeam'], row['AwayTeam']
        features.append([elo[h], elo[a], elo[h]-elo[a], corners[h], corners[a]])
        targets.append([row['FTHG'], row['FTAG'], row['HC'], row['AC']])
        
        # Update ratings
        actual = 1 if row['FTHG'] > row['FTAG'] else (0.5 if row['FTHG'] == row['FTAG'] else 0)
        expected = 1 / (1 + 10 ** ((elo[a] - elo[h]) / 400))
        shift = 30 * (actual - expected)
        elo[h] += shift; elo[a] -= shift
        corners[h] = (corners[h] * 0.9) + (row['HC'] * 0.1)
        corners[a] = (corners[a] * 0.9) + (row['AC'] * 0.1)

    # Train
    model = MultiOutputRegressor(xgb.XGBRegressor(tree_method='hist', n_estimators=100))
    model.fit(np.array(features, dtype=np.float32), np.array(targets, dtype=np.float32))

    # Save to models folder
    with open(os.getenv("MODEL_PATH"), 'wb') as f:
        pickle.dump({'model': model, 'elos': elo, 'corners': corners}, f)