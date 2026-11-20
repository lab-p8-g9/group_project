FROM python:3.11-slim

WORKDIR /app

COPY ./Logic_manager ./Logic_manager
COPY ./Data_manager ./Data_manager
COPY ./AI_manager ./AI_manager
COPY ./IO_manager ./IO_manager

RUN pip install --no-cache-dir pygarble python-dotenv openai flask

EXPOSE 8080

CMD ["flask", "--app", "IO_manager.io_manager", "run", "--host=0.0.0.0", "--port=8080"]