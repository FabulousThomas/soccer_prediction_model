#!/bin/bash
cd /home/ubuntu/soccer_project
source soccer_env/bin/activate
# Run the main orchestrator
python3 main.py >> logs/automation.log 2>&1