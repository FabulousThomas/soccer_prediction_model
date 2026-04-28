# Soccer Prediction Model

This project uses machine learning to predict soccer match outcomes based on team performance data.

## Features

- Machine learning model for predicting soccer match outcomes
- Real-time fixture data fetching from football-data.co.uk
- Telegram notifications for predictions
- CSV export of predictions
- Automatic model retraining

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env
# Edit .env with your Telegram token and chat ID
```

3. Run the prediction script:
```bash
python main.py
```

## Usage

The script will:
1. Fetch upcoming fixtures from football-data.co.uk
2. Make predictions for each match
3. Display results in the console
4. Send a summary to your Telegram chat
5. Save predictions to a CSV file

## Model

The model is trained on historical soccer data and uses features like:
- Team form and recent performance
- Head-to-head records
- League position
- Home/away advantage
- Goal-scoring statistics

## License

This project is for educational purposes only.
