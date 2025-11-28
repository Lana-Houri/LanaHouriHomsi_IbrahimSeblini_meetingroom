FROM python:3.11-slim

WORKDIR /app

# Copy shared_utils first (from parent directory)
COPY shared_utils /app/shared_utils

# Copy bookings service requirements and install dependencies
COPY bookings/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy bookings service application code
COPY bookings /app

# Expose port
EXPOSE 5002

# Run the application
CMD ["python", "app.py"]

