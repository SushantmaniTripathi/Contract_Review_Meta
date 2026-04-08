FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies first (layer caching)
COPY server/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project
COPY . .

# HF Spaces uses port 7860 by default; fall back to 8000 for local Docker
EXPOSE 7860

# Start the FastAPI server
# PORT env var is set by HF Spaces; default 7860 for local use
CMD ["sh", "-c", "uvicorn server.app:app --host 0.0.0.0 --port ${PORT:-7860}"]
