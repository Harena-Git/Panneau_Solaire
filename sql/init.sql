-- =============================================================
-- Panneau Solaire - SQL Server initialisation
-- =============================================================

-- Create database (skip if it already exists)
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = N'PanneauSolaire')
BEGIN
    CREATE DATABASE PanneauSolaire;
END
GO

USE PanneauSolaire;
GO

-- =============================================================
-- Table: panneaux
-- Stores basic information about each solar panel.
-- =============================================================
IF NOT EXISTS (
    SELECT * FROM sys.tables WHERE name = 'panneaux'
)
BEGIN
    CREATE TABLE panneaux (
        id            INT IDENTITY(1,1) PRIMARY KEY,
        nom           NVARCHAR(100)  NOT NULL,
        localisation  NVARCHAR(255)  NOT NULL,
        puissance_kw  DECIMAL(10, 2) NOT NULL,   -- rated power in kW
        statut        NVARCHAR(20)   NOT NULL DEFAULT 'actif'
                          CHECK (statut IN ('actif', 'maintenance', 'panne')),
        date_installation DATE        NOT NULL DEFAULT CAST(GETDATE() AS DATE),
        date_creation DATETIME2      NOT NULL DEFAULT GETDATE(),
        date_modification DATETIME2  NOT NULL DEFAULT GETDATE()
    );
END
GO

-- =============================================================
-- Table: productions
-- Stores periodic energy-production readings for each panel.
-- =============================================================
IF NOT EXISTS (
    SELECT * FROM sys.tables WHERE name = 'productions'
)
BEGIN
    CREATE TABLE productions (
        id           INT IDENTITY(1,1) PRIMARY KEY,
        panneau_id   INT            NOT NULL
                         REFERENCES panneaux(id) ON DELETE CASCADE,
        energie_kwh  DECIMAL(10, 4) NOT NULL,     -- energy produced in kWh
        temperature  DECIMAL(5, 2)  NULL,          -- panel temperature in °C
        irradiance   DECIMAL(8, 2)  NULL,          -- solar irradiance in W/m²
        horodatage   DATETIME2      NOT NULL DEFAULT GETDATE()
    );
END
GO

-- =============================================================
-- Table: alertes
-- Stores alerts / anomalies detected for each panel.
-- =============================================================
IF NOT EXISTS (
    SELECT * FROM sys.tables WHERE name = 'alertes'
)
BEGIN
    CREATE TABLE alertes (
        id           INT IDENTITY(1,1) PRIMARY KEY,
        panneau_id   INT            NOT NULL
                         REFERENCES panneaux(id) ON DELETE CASCADE,
        type_alerte  NVARCHAR(50)   NOT NULL
                         CHECK (type_alerte IN ('surchauffe', 'sous-production', 'panne', 'maintenance')),
        message      NVARCHAR(500)  NOT NULL,
        resolue      BIT            NOT NULL DEFAULT 0,
        horodatage   DATETIME2      NOT NULL DEFAULT GETDATE()
    );
END
GO

-- =============================================================
-- Seed data – sample panels
-- =============================================================
IF NOT EXISTS (SELECT TOP 1 id FROM panneaux)
BEGIN
    INSERT INTO panneaux (nom, localisation, puissance_kw, statut, date_installation)
    VALUES
        (N'Panneau A1', N'Toit Nord, Bâtiment A',  5.00, 'actif',        '2023-01-15'),
        (N'Panneau A2', N'Toit Nord, Bâtiment A',  5.00, 'actif',        '2023-01-15'),
        (N'Panneau B1', N'Toit Sud, Bâtiment B',   7.50, 'actif',        '2023-03-20'),
        (N'Panneau B2', N'Toit Sud, Bâtiment B',   7.50, 'maintenance',  '2023-03-20'),
        (N'Panneau C1', N'Parking, Zone C',        10.00, 'actif',        '2024-06-01');
END
GO

-- =============================================================
-- Seed data – sample production readings
-- =============================================================
IF NOT EXISTS (SELECT TOP 1 id FROM productions)
BEGIN
    INSERT INTO productions (panneau_id, energie_kwh, temperature, irradiance, horodatage)
    VALUES
        (1, 4.80, 45.2, 850.0, DATEADD(HOUR, -2, GETDATE())),
        (1, 4.95, 44.8, 870.0, DATEADD(HOUR, -1, GETDATE())),
        (2, 4.70, 46.0, 845.0, DATEADD(HOUR, -2, GETDATE())),
        (3, 7.20, 50.1, 900.0, DATEADD(HOUR, -2, GETDATE())),
        (5, 9.80, 38.5, 920.0, DATEADD(HOUR, -1, GETDATE()));
END
GO
