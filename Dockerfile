FROM python:3.12-slim

WORKDIR /app

COPY logic_manager.py .
COPY logic_test.py .

CMD ["python", "logic_test.py"]