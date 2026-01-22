FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY business_logic_service /app/business_logic_service

EXPOSE 8003
CMD ["uvicorn", "business_logic_service.main:app", "--host", "0.0.0.0", "--port", "8003"]
