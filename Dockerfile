FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app.py .

EXPOSE 8080

HEALTHCHECK CMD curl --fail http://localhost:8080/_stcore/health

CMD streamlit run --server.port=8080 --server.enableCORS false app.py