import streamlit as st
import pandas as pd
from datetime import date, datetime
from sqlalchemy import create_engine, text
import urllib

st.set_page_config(page_title="Accommodation Application", layout="centered")
st.title("Accommodation Application")
st.caption("Please complete the form below to apply for accommodation.")

# ---------------------------------------------------------------------------
# SQL Server connection (Windows Authentication)
# ---------------------------------------------------------------------------
SERVER = r"GHOST\MSSQLSERVER02"
DATABASE = "stg_booking_com"
TABLE = "dbo.stg_booking_com_raw"

@st.cache_resource
def get_engine():
    params = urllib.parse.quote_plus(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={SERVER};"
        f"DATABASE={DATABASE};"
        f"Trusted_Connection=yes;"
    )
    return create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

engine = get_engine()

# ---------------------------------------------------------------------------
# Form
# ---------------------------------------------------------------------------
with st.form("accommodation_form", clear_on_submit=True):

    st.subheader("Personal Details")
    col1, col2 = st.columns(2)
    with col1:
        full_name = st.text_input("Full Name *")
        id_number = st.text_input("ID / Passport Number *")
    with col2:
        email = st.text_input("Email Address *")
        phone = st.text_input("Phone Number *")

    st.subheader("Stay Details")
    col3, col4 = st.columns(2)
    with col3:
        check_in = st.date_input("Check-in Date *", min_value=date.today())
        room_type = st.selectbox("Room Type Preference", ["Single", "Shared/Double", "Family", "No preference"])
    with col4:
        check_out = st.date_input("Check-out Date *", min_value=date.today())
        num_guests = st.number_input("Number of Guests", min_value=1, max_value=10, value=1)

    st.subheader("Purpose of Stay")
    purpose = st.selectbox("Reason for Stay", ["Work", "Study", "Relocation", "Other"])
    organisation = st.text_input("Employer / Institution Name (if applicable)")

    st.subheader("Special Requirements")
    accessibility = st.text_area("Accessibility Needs (optional)")
    dietary = st.text_area("Dietary Restrictions (optional)")

    st.subheader("Emergency Contact")
    col5, col6 = st.columns(2)
    with col5:
        emergency_name = st.text_input("Emergency Contact Name *")
    with col6:
        emergency_phone = st.text_input("Emergency Contact Phone *")

    submitted = st.form_submit_button("Submit Application")

    if submitted:
        required = [full_name, id_number, email, phone, emergency_name, emergency_phone]

        # Table columns are NOT NULL and id_number/phone/emergency_phone are numeric,
        # so validate before attempting the insert.
        if not all(required):
            st.error("Please fill in all required fields marked with *.")
        elif check_out <= check_in:
            st.error("Check-out date must be after check-in date.")
        elif not id_number.isdigit():
            st.error("ID / Passport Number must be numeric (table column is bigint).")
        elif not phone.isdigit():
            st.error("Phone Number must be numeric (table column is int).")
        elif not emergency_phone.isdigit():
            st.error("Emergency Contact Phone must be numeric (table column is int).")
        else:
            record = {
                "submitted_at": datetime.now(),
                "full_name": full_name,
                "id_number": int(id_number),
                "email": email,
                "phone": int(phone),
                "check_in": check_in,
                "check_out": check_out,
                "room_type": room_type,
                "num_guests": int(num_guests),
                "purpose": purpose,
                "organisation": organisation,
                "accessibility": accessibility,
                "dietary": dietary,
                "emergency_name": emergency_name,
                "emergency_phone": int(emergency_phone),
            }

            try:
                insert_sql = text(f"""
                    INSERT INTO {TABLE}
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
                with engine.begin() as conn:
                    conn.execute(insert_sql, record)

                st.success(f"Thank you, {full_name}! Your application has been submitted.")
            except Exception as e:
                st.error(f"Failed to save to database: {e}")

# ---------------------------------------------------------------------------
# Admin view — reads straight from SQL Server
# ---------------------------------------------------------------------------
with st.expander("View submitted applications (admin)"):
    try:
        df = pd.read_sql(f"SELECT * FROM {TABLE} ORDER BY submitted_at DESC", engine)
        if df.empty:
            st.info("No applications submitted yet.")
        else:
            st.dataframe(df, use_container_width=True)
            st.download_button(
                "Download all applications (CSV)",
                df.to_csv(index=False).encode("utf-8"),
                file_name="applications.csv",
                mime="text/csv",
            )
    except Exception as e:
        st.error(f"Could not load data from database: {e}")