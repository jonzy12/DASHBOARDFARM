FROM python:3.11-slim

WORKDIR /app

# העתקת דרישות המערכת והתקנתן
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# העתקת קוד השרת
COPY ./back-end ./back-end

WORKDIR /app/back-end

EXPOSE 8000

# הרצת השרת של FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]