FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=8080
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && useradd --create-home appuser
COPY . .
RUN chown -R appuser:appuser /app
USER appuser
EXPOSE 8080
CMD exec gunicorn --bind :${PORT} --workers 1 --threads 8 --timeout 0 app:app
