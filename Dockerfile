# 1. Base image
FROM python:3.11-slim

# 2. Çalışma klasörü
WORKDIR /app

# 3. Gereksinimleri kopyala ve yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Uygulamayı kopyala
COPY . .

# 5. Cloud Run PORT ortam değişkeniyle dinle
ENV PORT 8080

# 6. Container başlatıldığında Flask'ı ayağa kaldır
CMD ["python", "obs_scraper.py"] 