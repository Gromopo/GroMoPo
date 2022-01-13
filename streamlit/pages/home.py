import streamlit as st
from utils import helpers as hp


def app():
	st.markdown(hp.read_markdown_file("/pages/view/home_page.md"), unsafe_allow_html=True)
	st.image("/pages/img/GroMoPohomebanner.png", caption=None, width=None, use_column_width=None, clamp=False, channels='RGB', output_format='auto')


