FROM python:3.12-slim

WORKDIR /app

COPY logic_manager.py .
COPY data_manager.py .
COPY ai_manager.py .
COPY io_manager.py .
COPY main.py .
COPY complaint.db .
COPY complaint.json .

RUN pip install --no-cache-dir pygarble python-dotenv openai

CMD ["python", "main.py"]