import streamlit as st
from utils import helpers as hp
from pathlib import Path

def app():
    main_path = Path("pages")
    markdown = hp.read_markdown_file(str(main_path.joinpath('view','about_page.md')))
    st.markdown(markdown, unsafe_allow_html=True)
