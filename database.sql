-- Create the database (run this only once)
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = N'database_db')
BEGIN
    CREATE DATABASE database_db;
END

-- Use the database
USE database_db;

-- Create the items table
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='items' AND xtype='U')
BEGIN
    CREATE TABLE items (
        item_id VARCHAR(255) PRIMARY KEY,
        name VARCHAR(255),
        quantity INT,
        price FLOAT
    );
    
END