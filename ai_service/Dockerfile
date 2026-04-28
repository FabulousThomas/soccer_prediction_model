# 1. Start with base
FROM python:3.10-slim

# 2. Set working directory
WORKDIR /app

# 3. Copy ONLY the requirements first
COPY requirements.txt .

# 4. Install libraries (This layer is cached unless requirements.txt changes)
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of your code (Only this part runs when you edit main.py)
COPY . .

# 6. Start the server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]