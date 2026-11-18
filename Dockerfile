FROM python:3.11-slim

WORKDIR /app

COPY ./Logic_manager ./Logic_manager
COPY ./Data_manager ./Data_manager
COPY ./AI_manager ./AI_manager
COPY ./IO_manager ./IO_manager

RUN pip install --no-cache-dir pygarble python-dotenv openai flask

EXPOSE 8080

CMD ["python", "IO_manager/io_manager.py"]