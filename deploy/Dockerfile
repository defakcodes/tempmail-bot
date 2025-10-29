FROM python:3.9-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files
COPY . .

# Create config directory
RUN mkdir -p config

# Default command
CMD ["python", "main.py", "all"]
