FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for MySQL
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

EXPOSE 8000

# sudo find / -type f -name "wsgi.py" 2>/dev/null
# /home/ubuntu/ApexBank/banking_project/wsgi.py path of gunicorn.
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "banking_project.wsgi:application"]