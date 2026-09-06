import streamlit as st
import pandas as pd
from datetime import date, datetime
import os

st.set_page_config(page_title="Accommodation Application", layout="centered")
st.title("Accommodation Application")
st.caption("Please complete the form below to apply for accommodation.")

DATA_FILE = "applications.csv"

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
        if not all(required):
            st.error("Please fill in all required fields marked with *.")
        elif check_out <= check_in:
            st.error("Check-out date must be after check-in date.")
        else:
            record = {
                "submitted_at": datetime.now().isoformat(timespec="seconds"),
                "full_name": full_name,
                "id_number": id_number,
                "email": email,
                "phone": phone,
                "check_in": check_in.isoformat(),
                "check_out": check_out.isoformat(),
                "room_type": room_type,
                "num_guests": num_guests,
                "purpose": purpose,
                "organisation": organisation,
                "accessibility": accessibility,
                "dietary": dietary,
                "emergency_name": emergency_name,
                "emergency_phone": emergency_phone,
            }
            df_new = pd.DataFrame([record])
            if os.path.exists(DATA_FILE):
                df_new.to_csv(DATA_FILE, mode="a", header=False, index=False)
            else:
                df_new.to_csv(DATA_FILE, index=False)

            st.success(f"Thank you, {full_name}! Your application has been submitted.")

# --- Admin view ---
with st.expander("View submitted applications (admin)"):
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        st.dataframe(df, use_container_width=True)
        st.download_button(
            "Download all applications (CSV)",
            df.to_csv(index=False).encode("utf-8"),
            file_name="applications.csv",
            mime="text/csv",
        )
    else:
        st.info("No applications submitted yet.")
