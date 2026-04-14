"""
database.py – SQL Server connection factory.

Connection parameters are read from environment variables (set via .env or
docker-compose.yml):

    DB_SERVER   SQL Server host / IP          (default: sqlserver)
    DB_PORT     SQL Server TCP port            (default: 1433)
    DB_NAME     Database name                  (default: PanneauSolaire)
    DB_USER     Login name                     (default: sa)
    DB_PASSWORD SA / user password             (required)
"""

import os
import pyodbc


def get_connection() -> pyodbc.Connection:
    """Return an open pyodbc connection to the SQL Server database."""
    server   = os.getenv("DB_SERVER",   "sqlserver")
    port     = os.getenv("DB_PORT",     "1433")
    database = os.getenv("DB_NAME",     "PanneauSolaire")
    username = os.getenv("DB_USER",     "sa")
    password = os.getenv("DB_PASSWORD", "")

    conn_str = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER={server},{port};"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password};"
        "TrustServerCertificate=yes;"
        "Encrypt=yes;"
    )
    return pyodbc.connect(conn_str, timeout=30)
