FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY adapter_service /app/adapter_service

EXPOSE 8002
CMD ["uvicorn", "adapter_service.main:app", "--host", "0.0.0.0", "--port", "8002"]
