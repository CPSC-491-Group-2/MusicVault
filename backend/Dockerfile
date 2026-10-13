
# syntax=docker/dockerfile:1
FROM python:3.13-slim

WORKDIR /app

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy the main Flask backend.
COPY backend/ ./

# Copy the reusable Spotify service and parsers.
COPY spotify-api-backend/services/ ./spotify_api_lib/services/
COPY spotify-api-backend/spotify/ ./spotify_api_lib/spotify/

# Allow Python to import the standalone Spotify modules.
ENV PYTHONPATH=/app:/app/spotify_api_lib

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]
