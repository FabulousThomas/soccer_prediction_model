from src.fetch_data import download_data
from src.train import train_model
from src.notify import send_alert
from src.fixtures import get_upcoming_fixtures
from src.batch_predict import run_weekend_analysis, send_summary_to_telegram

def run_pipeline():
    try:
        send_alert("🚀 *Update Started:* Fetching new 2026 data...")
        download_data()
        
        send_alert("🧠 *Retraining:* Updating Elo and Corner styles...")
        train_model()
        
        send_alert("✅ *Success:* Model is updated and ready for next week!")
        
        # 2. Get Matches Automatically
        upcoming = get_upcoming_fixtures()
        
        if upcoming:
            # 3. Predict & Alert
            results = run_weekend_analysis(upcoming)
            send_summary_to_telegram(results)
            print("🏁 Pipeline complete: Predictions sent to Telegram.")
        else:
            print("System: No upcoming fixtures found for this week.")
        # ------------------------------------------

        send_alert("✅ *Success:* Model updated and Preview sent!")
        
    except Exception as e:
        send_alert(f"⚠️ *Error:* Pipeline failed. Check logs.\n`{str(e)}` ")

if __name__ == "__main__":
    run_pipeline()