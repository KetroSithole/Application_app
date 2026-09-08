-- Run this once against your SQL Server instance (master context).
IF NOT EXISTS (SELECT 1 FROM sys.databases WHERE name = N'stg_booking_com')
BEGIN
    CREATE DATABASE stg_booking_com;
END
GO
