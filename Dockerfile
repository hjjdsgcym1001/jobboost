FROM python:3.11-slim

WORKDIR /app

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Use PORT env var (Railway sets this automatically)
EXPOSE 8000

CMD ["python", "run.py"]