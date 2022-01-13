import streamlit as st
from utils import helpers as hp
from pathlib import Path


def app():
    main_path = Path("pages")
    st.markdown(hp.read_markdown_file(str(main_path.joinpath('view','home_page.md'))), unsafe_allow_html=True)
    st.image(str(main_path.joinpath('img','GroMoPohomebanner.png')), caption=None,
          width=None, use_column_width=None,clamp=False, channels='RGB', output_format='auto')


