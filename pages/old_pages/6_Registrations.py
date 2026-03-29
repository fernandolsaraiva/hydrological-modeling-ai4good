import streamlit as st
from PIL import Image
from util import get_station_names_and_critical_levels, email_exists, insert_user_info
import pandas as pd
import os
from util import get_station_names_and_critical_levels

def main():
    st.title("User Registration")
    
    st.write("Do you live near any of these stations? We are monitoring the possibility of flooding. If the levels become critical, we will issue an alert to you.")
    
    # Display images in the sidebar
    logo_ifast = Image.open("img/logo_ifast.png")
    st.sidebar.image(logo_ifast, width=200)
    logo_ai4good = Image.open("img/logo_ai4good.png")
    st.sidebar.image(logo_ai4good, width=150)
    
    # Create the registration form
    with st.form("registration_form"):
        name = st.text_input("Name")
        number = st.text_input("Number")
        email = st.text_input("Email")
        
        # Station selection using the imported function
        station_names, critical_levels = get_station_names_and_critical_levels()
        default_station = "Rio Tamanduateí - Mercado Municipal"
        if default_station in station_names:
            station = st.selectbox("Select the station", station_names, index=station_names.index(default_station))
        else:
            station = st.selectbox("Select the station", station_names)
        
        submit = st.form_submit_button("Register")
    
    if submit:
        # Validate the email format: must contain '@' and a '.' after '@'
        if "@" not in email or "." not in email or email.rfind('.') < email.find('@'):
            st.error("The email format is incorrect. Please enter a valid email address.")
        # Check if the email is already registered in the database
        elif email_exists(email):
            st.error("This email has already been registered.")
        else:
            success, msg = insert_user_info(name, number, email, station)
        if success:
            st.success(msg)
        else:
            st.error(msg)

if __name__ == "__main__":
    main()
