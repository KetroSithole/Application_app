-- Run against the stg_booking_com database (matches ACCOMMODATION_DATABASE / ACCOMMODATION_TABLE in .env).
USE stg_booking_com;
GO

IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'stg_booking_com_raw' AND schema_id = SCHEMA_ID('dbo'))
BEGIN
    CREATE TABLE dbo.stg_booking_com_raw (
        id                INT IDENTITY(1,1) PRIMARY KEY,
        submitted_at      DATETIME2      NOT NULL,
        full_name         NVARCHAR(200)  NOT NULL,
        id_number         BIGINT         NOT NULL,
        email             NVARCHAR(255)  NOT NULL,
        phone             INT            NOT NULL,
        check_in          DATE           NOT NULL,
        check_out         DATE           NOT NULL,
        room_type         NVARCHAR(50)   NOT NULL,
        num_guests        INT            NOT NULL,
        purpose           NVARCHAR(50)   NOT NULL,
        organisation      NVARCHAR(200)  NULL,
        accessibility     NVARCHAR(MAX)  NULL,
        dietary           NVARCHAR(MAX)  NULL,
        emergency_name    NVARCHAR(200)  NOT NULL,
        emergency_phone   INT            NOT NULL
    );
END
GO
