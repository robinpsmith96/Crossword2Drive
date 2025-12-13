FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

# Upgrade pip and force install latest versions
RUN pip install --upgrade pip \
    && pip install --no-cache-dir --upgrade -r requirements.txt

COPY app.py .

CMD ["python", "app.py"]
