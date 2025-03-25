import streamlit as st
from PIL import Image
from util import get_station_names_and_critical_levels, email_exists, insert_user_info

import streamlit as st
import pandas as pd
import os
from PIL import Image
from util import get_last_available_date, get_station_code_flu, get_station_data_flu, get_station_names_and_critical_levels

def main():
    st.title("User Registration")
    
    st.write("Do you live near any of these stations? We are monitoring the possibility of flooding. If the levels become critical, we will issue an alert to you.")
    
    # Display images in the sidebar
    logo_ifast = Image.open("img/logo_ifast.png")
    st.sidebar.image(logo_ifast, width=200)
    logo_ai4good = Image.open("img/logo_ai4good.png")
    st.sidebar.image(logo_ai4good, width=150)
    
    csv_file = "registrations.csv"
    
    # Load existing registrations or create a new DataFrame if the file doesn't exist.
    if os.path.exists(csv_file):
        registrations_df = pd.read_csv(csv_file)
    else:
        registrations_df = pd.DataFrame(columns=["Name", "Number", "Email", "Station"])
    
    # Create a registration form.
    with st.form("registration_form"):
        name = st.text_input("Name")
        number = st.text_input("Number")
        email = st.text_input("Email")
        
        # Station selection using the imported function.
        station_names, critical_levels = get_station_names_and_critical_levels()
        default_station = "Rio Tamanduateí - Mercado Municipal"
        if default_station in station_names:
            station = st.selectbox("Select the station", station_names, index=station_names.index(default_station))
        else:
            station = st.selectbox("Select the station", station_names)
        
        submit = st.form_submit_button("Register")
    
    if submit:
        # Basic email format validation: it must contain '@' and a dot after '@'
        if "@" not in email or "." not in email or email.rfind('.') < email.find('@'):
            st.error("The email format is incorrect. Please enter a valid email address.")
        # Check if the email has already been registered.
        elif email in registrations_df["Email"].values:
            st.error("This email has already been registered.")
        else:
            new_registration = {"Name": name, "Number": number, "Email": email, "Station": station}
            registrations_df = registrations_df.append(new_registration, ignore_index=True)
            registrations_df.to_csv(csv_file, index=False)
            st.success("Registration successful!")

if __name__ == "__main__":
    main()
