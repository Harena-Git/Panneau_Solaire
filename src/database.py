import pyodbc
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    """Crée et retourne une connexion à SQL Server"""
    server = os.getenv('DB_SERVER')
    port = os.getenv('DB_PORT')
    database = os.getenv('DB_NAME')
    username = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    driver = os.getenv('DB_DRIVER')
    
    connection_string = (
        f'DRIVER={driver};'
        f'SERVER={server},{port};'
        f'DATABASE={database};'
        f'UID={username};'
        f'PWD={password}'
    )
    
    try:
        conn = pyodbc.connect(connection_string)
        print("✓ Connexion réussie à SQL Server")
        return conn
    except Exception as e:
        print(f"✗ Erreur de connexion: {e}")
        return None

def test_connection():
    """Teste la connexion à la base de données"""
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT @@VERSION")
        row = cursor.fetchone()
        print(f"Version SQL Server: {row[0][:50]}...")
        cursor.close()
        conn.close()
    return conn is not None