from database import get_connection

def create_table():
    """Crée une table d'exemple"""
    conn = get_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    # Créer une base de données de test
    cursor.execute("IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'TestDB') CREATE DATABASE TestDB")
    cursor.execute("USE TestDB")
    
    # Créer une table
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Users')
        CREATE TABLE Users (
            id INT PRIMARY KEY IDENTITY(1,1),
            nom NVARCHAR(100),
            email NVARCHAR(100),
            date_creation DATETIME DEFAULT GETDATE()
        )
    """)
    
    conn.commit()
    print("✓ Table 'Users' créée")
    cursor.close()
    conn.close()

def insert_data():
    """Insère des données d'exemple"""
    conn = get_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    cursor.execute("USE TestDB")
    
    cursor.execute("""
        INSERT INTO Users (nom, email) 
        VALUES (?, ?)
    """, ('Jean Dupont', 'jean@example.com'))
    
    conn.commit()
    print("✓ Données insérées")
    cursor.close()
    conn.close()

def read_data():
    """Lit et affiche les données"""
    conn = get_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    cursor.execute("USE TestDB")
    cursor.execute("SELECT * FROM Users")
    
    rows = cursor.fetchall()
    print("\n=== Données dans Users ===")
    for row in rows:
        print(f"ID: {row.id}, Nom: {row.nom}, Email: {row.email}")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    print("🚀 Démarrage du projet Python + SQL Server\n")
    create_table()
    insert_data()
    read_data()
    print("\n✓ Tests terminés avec succès!")