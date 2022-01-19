import streamlit as st
from utils import helpers as hp
from pathlib import Path
import platform

def app():
    if platform.system() == 'Windows':
        main_path = Path(".")
    else:
        main_path = Path("streamlit")
        
    markdown = hp.read_markdown_file(str(main_path.joinpath('pages','view','about_page.md')))
    st.markdown(markdown, unsafe_allow_html=True)
