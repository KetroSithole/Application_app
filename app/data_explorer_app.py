import streamlit as st
import pandas as pd

from config import SQL_SERVER, SQL_DRIVER, get_pyodbc_connection, get_sqlalchemy_engine

st.set_page_config(page_title="Data Explorer", page_icon="🗂️", layout="wide")

# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    .main .block-container { padding-top: 2rem; max-width: 1100px; }

    h1 { font-weight: 700; letter-spacing: -0.02em; }
    h1 span.accent { color: #6C63FF; }

    .subtitle { color: #6b7280; font-size: 1rem; margin-top: -0.6rem; margin-bottom: 1.5rem; }

    div[data-testid="stMetric"] {
        background: #f8f9fb;
        border: 1px solid #eceef2;
        border-radius: 10px;
        padding: 0.8rem 1rem;
    }

    .stTabs [data-baseweb="tab-list"] { gap: 4px; }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 8px 18px;
        font-weight: 600;
    }

    div[data-testid="stForm"], .stExpander {
        border: 1px solid #eceef2;
        border-radius: 12px;
        padding: 0.5rem;
    }

    button[kind="primary"], .stButton>button {
        border-radius: 8px;
        font-weight: 600;
    }

    div[data-testid="stFileUploader"] {
        border: 1.5px dashed #c7c9d9;
        border-radius: 12px;
        padding: 0.5rem;
    }

    .status-card {
        border-radius: 10px;
        padding: 0.9rem 1.1rem;
        margin: 0.6rem 0;
        font-size: 0.95rem;
    }
    .status-ok { background: #ecfdf3; border: 1px solid #b7ebc6; color: #1a7f37; }
    .status-err { background: #fef2f2; border: 1px solid #f5b5b5; color: #b42318; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("# 🗂️ Data <span class='accent'>Explorer</span>", unsafe_allow_html=True)
st.markdown(
    "<div class='subtitle'>Upload a CSV, push it into SQL Server, or browse what's already there.</div>",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Sidebar — connection settings (shared across tabs)
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🔌 Connection")
    st.caption(f"Server\n\n**{SQL_SERVER}**\n\nWindows Authentication")
    database = st.text_input("Database name", value="")
    driver = st.selectbox(
        "ODBC Driver",
        ["ODBC Driver 17 for SQL Server", "ODBC Driver 18 for SQL Server", "SQL Server"],
        index=["ODBC Driver 17 for SQL Server", "ODBC Driver 18 for SQL Server", "SQL Server"].index(SQL_DRIVER)
        if SQL_DRIVER in ["ODBC Driver 17 for SQL Server", "ODBC Driver 18 for SQL Server", "SQL Server"]
        else 0,
    )
    trust_cert = st.checkbox("Trust server certificate (Driver 18 only)", value=True)
    st.divider()
    st.caption("Connection is reused across both tabs.")


@st.cache_data(ttl=300)
def run_query(db_name: str, query: str, driver: str, trust_cert: bool) -> pd.DataFrame:
    with get_pyodbc_connection(db_name, driver, trust_cert) as conn:
        return pd.read_sql(query, conn)


@st.cache_data(ttl=300)
def list_tables(db_name: str, driver: str, trust_cert: bool) -> pd.DataFrame:
    query = """
        SELECT TABLE_SCHEMA, TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_SCHEMA, TABLE_NAME
    """
    return run_query(db_name, query, driver, trust_cert)


tab_load, tab_browse = st.tabs(["⬆️  Load CSV into Database", "🔍  Browse Database"])

# ---------------------------------------------------------------------------
# TAB 1 — Upload CSV and push into SQL Server
# ---------------------------------------------------------------------------
with tab_load:
    st.markdown("#### Upload a CSV file")
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"], label_visibility="collapsed")

    if uploaded_file is not None:
        try:
            csv_df = pd.read_csv(uploaded_file)
        except Exception as e:
            st.markdown(f"<div class='status-card status-err'>Could not read CSV: {e}</div>", unsafe_allow_html=True)
            csv_df = None

        if csv_df is not None:
            c1, c2, c3 = st.columns(3)
            c1.metric("Rows", f"{len(csv_df):,}")
            c2.metric("Columns", len(csv_df.columns))
            c3.metric("File", uploaded_file.name)

            st.dataframe(csv_df.head(50), use_container_width=True)

            st.markdown("#### Push into SQL Server")
            if not database:
                st.info("Enter a database name in the sidebar first.")
            else:
                col1, col2 = st.columns([2, 1])
                with col1:
                    table_name = st.text_input(
                        "Target table name",
                        value=uploaded_file.name.rsplit(".", 1)[0].replace(" ", "_"),
                    )
                with col2:
                    if_exists = st.selectbox("If table exists", ["append", "replace", "fail"])

                if st.button("🚀 Load into database", type="primary"):
                    try:
                        engine = get_sqlalchemy_engine(database, driver, trust_cert)
                        with st.spinner(f"Writing {len(csv_df):,} rows to {table_name}..."):
                            csv_df.to_sql(table_name, engine, if_exists=if_exists, index=False)
                        st.markdown(
                            f"<div class='status-card status-ok'>✅ Loaded {len(csv_df):,} rows into "
                            f"<b>{database}.{table_name}</b>.</div>",
                            unsafe_allow_html=True,
                        )
                        list_tables.clear()
                    except Exception as e:
                        st.markdown(
                            f"<div class='status-card status-err'>❌ Load failed: {e}</div>",
                            unsafe_allow_html=True,
                        )
    else:
        st.info("👆 Upload a CSV to preview it and load it into the database.")

# ---------------------------------------------------------------------------
# TAB 2 — Browse existing database
# ---------------------------------------------------------------------------
with tab_browse:
    if not database:
        st.info("Enter a database name in the sidebar to connect.")
    else:
        try:
            tables_df = list_tables(database, driver, trust_cert)
        except Exception as e:
            st.markdown(f"<div class='status-card status-err'>Connection failed: {e}</div>", unsafe_allow_html=True)
            tables_df = None

        if tables_df is not None:
            sub1, sub2 = st.tabs(["Browse table", "Custom SQL"])

            with sub1:
                if tables_df.empty:
                    st.warning("No tables found in this database.")
                else:
                    tables_df["full_name"] = tables_df["TABLE_SCHEMA"] + "." + tables_df["TABLE_NAME"]
                    selected = st.selectbox("Table", tables_df["full_name"])
                    row_limit = st.slider("Rows to preview", 10, 1000, 100)

                    if selected:
                        query = f"SELECT TOP {row_limit} * FROM {selected}"
                        try:
                            db_df = run_query(database, query, driver, trust_cert)
                            st.dataframe(db_df, use_container_width=True)
                            st.caption(f"{len(db_df)} rows shown from {selected}")
                        except Exception as e:
                            st.markdown(f"<div class='status-card status-err'>Query failed: {e}</div>", unsafe_allow_html=True)

            with sub2:
                default_sql = "SELECT TOP 100 * FROM your_table"
                sql = st.text_area("SQL query", value=default_sql, height=150)
                if st.button("Run query"):
                    try:
                        db_df = run_query(database, sql, driver, trust_cert)
                        st.dataframe(db_df, use_container_width=True)
                        st.caption(f"{len(db_df)} rows returned")
                        st.download_button(
                            "Download CSV",
                            db_df.to_csv(index=False).encode("utf-8"),
                            file_name="query_result.csv",
                            mime="text/csv",
                        )
                    except Exception as e:
                        st.markdown(f"<div class='status-card status-err'>Query failed: {e}</div>", unsafe_allow_html=True)
