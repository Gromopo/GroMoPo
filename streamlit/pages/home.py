import streamlit as st
from utils import helpers as hp
from pathlib import Path
import platform


def app():
    if platform.system() == 'Darwin':
        main_path = Path("streamlit")
    else:
        main_path = Path(".")
    st.markdown(hp.read_markdown_file(str(main_path.joinpath('pages','view','home_page.md'))), unsafe_allow_html=True)
    st.image(str(main_path.joinpath('pages','img','GroMoPohomebanner.png')), caption=None,
          width=None, use_column_width=None,clamp=False, channels='RGB', output_format='auto')


