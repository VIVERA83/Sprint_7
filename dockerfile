FROM python:3.10.4-slim-buster
WORKDIR fastapi_solution
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV UVICORN_ARGS "main:app --host 0.0.0.0 --port 8000 --workers 3"

RUN pip install --upgrade pip  --no-cache-dir
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY fastapi_solution .
CMD uvicorn $UVICORN_ARGS
