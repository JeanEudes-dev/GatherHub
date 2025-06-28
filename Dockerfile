# --- Frontend build stage ---
FROM node:20 AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# --- Backend build stage ---
FROM python:3.11-slim AS backend-build
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY backend/requirements.prod.txt .
RUN pip install --upgrade pip && pip install -r requirements.prod.txt

# Copy backend code
COPY backend/ ./

# Copy frontend build output to Django static directory
COPY --from=frontend-build /app/frontend/dist ./static/

# --- Final stage ---
FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

# Install runtime dependencies
COPY --from=backend-build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-build /app /app

# Expose port
EXPOSE 8000

# Collect static files and run migrations at container start
CMD python manage.py collectstatic --noinput && python manage.py migrate && gunicorn --bind 0.0.0.0:8000 --workers 3 --worker-class uvicorn.workers.UvicornWorker gatherhub.asgi:application
