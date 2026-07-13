import streamlit as st
from PIL import Image

def main():
    st.title("About Us")
    
    st.write("""

    We are a group of people from the Brazilian northeast region living near the city of São Paulo, concerned about social problems that affect many people in different urban centers, and hopeful that Artificial Intelligence tools can accelerate and democratize solutions.

    Our project presents the first operational tool for predicting urban floods using explainable Artificial Intelligence. We exclusively use open-source tools, with real-time execution, a user-friendly interface, and a scalable approach. We count on the support of the AI4Good Brazil Conference to boost our platform and help us helping more and more people.
    """)

    st.write("### Meet Our Team")
    
    col1, col2, col3 = st.columns(3)
    
    def resize_image(image_path, size):
        img = Image.open(image_path)
        resized_img = img.resize(size)
        return resized_img
    
    size = (200, 200)  # Define the size (width, height)
    
    with col1:
        img1 = "img/fernando_saraiva.png"
        st.image(img1, caption="Fernando Saraiva holds a Bachelor's degree in Electronic Engineering from the Aeronautics Institute of Technology (ITA) and is pursuing a Master's degree in Computer Science with a focus on Machine Learning at the Federal University of São Paulo (Unifesp). He works as a data scientist specializing in artificial intelligence applications in renewable energy.",width=240)
    
    with col2:
        img2 = "img/luan_barauna.jpeg"
        st.image(img2, caption="Luan Baraúna holds a Bachelor's and Master's in Physics from the Federal University of Bahia (UFBA), and a Ph.D. in Applied Computing from the National Institute for Space Research (INPE), where he specialized in Artificial Intelligence (AI), developing a neural network for detecting patterns in the Fourier space.",width=280)
    
    with col3:
        img3 = "img/leonardo_santos.jpeg"
        st.image(img3, caption="Leonardo Santos is a Titular Researcher in Computational Modeling at CEMADEN-MCTI, a permanent professor in INPE's Applied Computing Graduate Program, and a collaborating professor in UNIFESP's Computer Science Graduate Program. Santos has a bachelor's in Physics from UFBA, a master's and PhD from INPE, and was a Visiting Professor at the Physics department at Humboldt University (Berlin).",width=250)



if __name__ == "__main__":
    main()