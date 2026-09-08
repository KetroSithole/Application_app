"""Seed dbo.stg_booking_com_raw with sample data, using the same .env config as the apps.

Run: python app/seed.py
"""
from datetime import date, datetime

from sqlalchemy import text

from config import ACCOMMODATION_DATABASE, ACCOMMODATION_TABLE, get_sqlalchemy_engine

SAMPLE_ROWS = [
    dict(submitted_at=datetime.now(), full_name="Jane Doe", id_number=9001015800086,
         email="jane.doe@example.com", phone=821234567,
         check_in=date(2026, 10, 1), check_out=date(2026, 10, 5), room_type="Single",
         num_guests=1, purpose="Work", organisation="Acme Corp",
         accessibility=None, dietary="Vegetarian",
         emergency_name="John Doe", emergency_phone=831234567),

    dict(submitted_at=datetime.now(), full_name="Sipho Nkosi", id_number=8805126800081,
         email="sipho.nkosi@example.com", phone=731234567,
         check_in=date(2026, 10, 3), check_out=date(2026, 10, 10), room_type="Shared/Double",
         num_guests=2, purpose="Study", organisation="University of Example",
         accessibility=None, dietary=None,
         emergency_name="Thandi Nkosi", emergency_phone=741234567),

    dict(submitted_at=datetime.now(), full_name="Amara Okafor", id_number=9210039800083,
         email="amara.okafor@example.com", phone=611234567,
         check_in=date(2026, 11, 1), check_out=date(2026, 11, 3), room_type="Family",
         num_guests=4, purpose="Relocation", organisation=None,
         accessibility="Wheelchair access required", dietary="Halal",
         emergency_name="Chidi Okafor", emergency_phone=621234567),

    dict(submitted_at=datetime.now(), full_name="Liam Smith", id_number=8709087800082,
         email="liam.smith@example.com", phone=721234567,
         check_in=date(2026, 9, 20), check_out=date(2026, 9, 25), room_type="No preference",
         num_guests=1, purpose="Other", organisation=None,
         accessibility=None, dietary=None,
         emergency_name="Emma Smith", emergency_phone=761234567),
]

INSERT_SQL = text(f"""
    INSERT INTO {ACCOMMODATION_TABLE}
        (submitted_at, full_name, id_number, email, phone,
         check_in, check_out, room_type, num_guests, purpose,
         organisation, accessibility, dietary,
         emergency_name, emergency_phone)
    VALUES
        (:submitted_at, :full_name, :id_number, :email, :phone,
         :check_in, :check_out, :room_type, :num_guests, :purpose,
         :organisation, :accessibility, :dietary,
         :emergency_name, :emergency_phone)
""")


def main():
    engine = get_sqlalchemy_engine(ACCOMMODATION_DATABASE)
    with engine.begin() as conn:
        existing = conn.execute(text(f"SELECT COUNT(*) FROM {ACCOMMODATION_TABLE}")).scalar()
        if existing:
            print(f"{ACCOMMODATION_TABLE} already has {existing} row(s) — skipping seed.")
            return
        conn.execute(INSERT_SQL, SAMPLE_ROWS)
    print(f"Seeded {len(SAMPLE_ROWS)} row(s) into {ACCOMMODATION_TABLE}.")


if __name__ == "__main__":
    main()
