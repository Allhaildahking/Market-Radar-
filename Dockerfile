FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY market_radar ./market_radar
COPY .env.example ./
ENV PYTHONUNBUFFERED=1
CMD ["python", "-m", "market_radar"]
