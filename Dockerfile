FROM apache/airflow:2.11.0-python3.11

COPY requirements.txt .

RUN pip install -r requirements.txt
