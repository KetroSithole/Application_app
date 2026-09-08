"""Shared SQL Server configuration, loaded from environment variables (.env)."""
import urllib.parse
from pathlib import Path

from dotenv import load_dotenv
import os

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

SQL_SERVER = os.getenv("SQL_SERVER", r"GHOST\MSSQLSERVER02")
SQL_DRIVER = os.getenv("SQL_DRIVER", "ODBC Driver 17 for SQL Server")

ACCOMMODATION_DATABASE = os.getenv("ACCOMMODATION_DATABASE", "stg_booking_com")
ACCOMMODATION_TABLE = os.getenv("ACCOMMODATION_TABLE", "dbo.stg_booking_com_raw")


def build_odbc_connection_string(database: str, driver: str = SQL_DRIVER, trust_cert: bool = False) -> str:
    conn_str = (
        f"DRIVER={{{driver}}};"
        f"SERVER={SQL_SERVER};"
        f"DATABASE={database};"
        f"Trusted_Connection=yes;"
    )
    if trust_cert and driver == "ODBC Driver 18 for SQL Server":
        conn_str += "TrustServerCertificate=yes;"
    return conn_str


def get_sqlalchemy_engine(database: str, driver: str = SQL_DRIVER, trust_cert: bool = False):
    from sqlalchemy import create_engine

    params = urllib.parse.quote_plus(build_odbc_connection_string(database, driver, trust_cert))
    return create_engine(f"mssql+pyodbc:///?odbc_connect={params}")


def get_pyodbc_connection(database: str, driver: str = SQL_DRIVER, trust_cert: bool = False):
    import pyodbc

    return pyodbc.connect(build_odbc_connection_string(database, driver, trust_cert))
