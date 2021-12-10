import streamlit as st
from utils import helpers as hp


def app():
	markdown = hp.read_markdown_file("pages/view/submit_page.md")
	st.markdown(markdown, unsafe_allow_html=True)  
