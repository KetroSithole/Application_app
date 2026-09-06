import streamlit as st
import pandas as pd
import pyodbc

st.set_page_config(page_title="SQL Server Explorer", layout="wide")
st.title("SQL Server Data Explorer")

SERVER = r"GHOST\MSSQLSERVER02"

# --- Sidebar: connection settings ---
st.sidebar.header("Connection")
database = st.sidebar.text_input("Database name", value="")
driver = st.sidebar.selectbox(
    "ODBC Driver",
    ["ODBC Driver 17 for SQL Server", "ODBC Driver 18 for SQL Server", "SQL Server"],
)
trust_cert = st.sidebar.checkbox("Trust server certificate (Driver 18 only)", value=True)


def get_connection(database: str):
    conn_str = (
        f"DRIVER={{{driver}}};"
        f"SERVER={SERVER};"
        f"DATABASE={database};"
        f"Trusted_Connection=yes;"
    )
    if driver == "ODBC Driver 18 for SQL Server" and trust_cert:
        conn_str += "TrustServerCertificate=yes;"
    return pyodbc.connect(conn_str)


@st.cache_data(ttl=300)
def run_query(database: str, query: str) -> pd.DataFrame:
    with get_connection(database) as conn:
        return pd.read_sql(query, conn)


@st.cache_data(ttl=300)
def list_tables(database: str) -> pd.DataFrame:
    query = """
        SELECT TABLE_SCHEMA, TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_SCHEMA, TABLE_NAME
    """
    return run_query(database, query)


if not database:
    st.info("Enter a database name in the sidebar to get started.")
    st.stop()

try:
    tables_df = list_tables(database)
except Exception as e:
    st.error(f"Connection failed: {e}")
    st.stop()

tab1, tab2 = st.tabs(["Browse table", "Custom SQL"])

with tab1:
    if tables_df.empty:
        st.warning("No tables found in this database.")
    else:
        tables_df["full_name"] = tables_df["TABLE_SCHEMA"] + "." + tables_df["TABLE_NAME"]
        selected = st.selectbox("Table", tables_df["full_name"])
        row_limit = st.slider("Rows to preview", 10, 1000, 100)

        if selected:
            query = f"SELECT TOP {row_limit} * FROM {selected}"
            try:
                df = run_query(database, query)
                st.dataframe(df, use_container_width=True)
                st.caption(f"{len(df)} rows shown from {selected}")
            except Exception as e:
                st.error(f"Query failed: {e}")

with tab2:
    default_sql = "SELECT TOP 100 * FROM your_table"
    sql = st.text_area("SQL query", value=default_sql, height=150)
    if st.button("Run query"):
        try:
            df = run_query(database, sql)
            st.dataframe(df, use_container_width=True)
            st.caption(f"{len(df)} rows returned")
            st.download_button(
                "Download CSV",
                df.to_csv(index=False).encode("utf-8"),
                file_name="query_result.csv",
                mime="text/csv",
            )
        except Exception as e:
            st.error(f"Query failed: {e}")
