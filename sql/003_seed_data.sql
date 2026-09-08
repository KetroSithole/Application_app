-- Sample/fake rows for local dev and testing. Safe to re-run (skips if already seeded).
USE stg_booking_com;
GO

IF NOT EXISTS (SELECT 1 FROM dbo.stg_booking_com_raw)
BEGIN
    INSERT INTO dbo.stg_booking_com_raw
        (submitted_at, full_name, id_number, email, phone,
         check_in, check_out, room_type, num_guests, purpose,
         organisation, accessibility, dietary,
         emergency_name, emergency_phone)
    VALUES
        (SYSDATETIME(), 'Jane Doe',    9001015800086, 'jane.doe@example.com',    821234567,
         '2026-10-01', '2026-10-05', 'Single',        1, 'Work',
         'Acme Corp', NULL, 'Vegetarian',
         'John Doe', 831234567),

        (SYSDATETIME(), 'Sipho Nkosi', 8805126800081, 'sipho.nkosi@example.com', 731234567,
         '2026-10-03', '2026-10-10', 'Shared/Double', 2, 'Study',
         'University of Example', NULL, NULL,
         'Thandi Nkosi', 741234567),

        (SYSDATETIME(), 'Amara Okafor', 9210039800083, 'amara.okafor@example.com', 611234567,
         '2026-11-01', '2026-11-03', 'Family',        4, 'Relocation',
         NULL, 'Wheelchair access required', 'Halal',
         'Chidi Okafor', 621234567),

        (SYSDATETIME(), 'Liam Smith',  8709087800082, 'liam.smith@example.com',  721234567,
         '2026-09-20', '2026-09-25', 'No preference', 1, 'Other',
         NULL, NULL, NULL,
         'Emma Smith', 761234567);
END
GO
