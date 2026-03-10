FROM python:3.12-slim

WORKDIR /app

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright's Chromium + all its system dependencies
RUN playwright install chromium --with-deps

# App code
COPY scraper/ ./scraper/
COPY backend/ ./backend/

RUN mkdir -p /app/data

COPY start.sh .
RUN chmod +x start.sh

CMD ["/bin/sh", "start.sh"]
