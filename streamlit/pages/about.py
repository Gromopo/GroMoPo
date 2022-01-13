import streamlit as st
from utils import helpers as hp
from pathlib import Path
import platform

def app():
    if platform.system() == 'Darwin':
        main_path = Path("streamlit")
    else:
        main_path = Path(".")
        
    markdown = hp.read_markdown_file(str(main_path.joinpath('pages','view','about_page.md')))
    st.markdown(markdown, unsafe_allow_html=True)
