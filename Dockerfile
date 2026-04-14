# ---------------------------------------------------------------------------
# Panneau Solaire – Python application image
# ---------------------------------------------------------------------------
FROM python:3.12-slim

# --- Install Microsoft ODBC Driver 18 for SQL Server ---
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl gnupg unixodbc-dev \
    && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc \
        | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
    && curl -fsSL https://packages.microsoft.com/config/debian/12/prod.list \
        -o /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql18 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /panneau_solaire

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

# Default command: show help (override with docker run / docker-compose)
CMD ["python", "-m", "app.main", "--help"]
