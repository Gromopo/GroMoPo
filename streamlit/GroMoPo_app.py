import streamlit as st

# Our app libs - possibly move to own folder
# from utils import helpers
from utils.multipage import MultiPage
from pages import home, about, submit_model, model_finder
from pathlib import Path
import platform

from streamlit_option_menu import option_menu

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

app = MultiPage()
#app.add_page("Home", home.app) # Name, Function
app.add_page("Home", model_finder.app)
app.add_page("Submit Model", submit_model.app)
app.add_page("About", about.app)

selected = option_menu(None, ["Home", "Submit Model", 'About'], 
    icons=['house', 'cloud-upload', 'gear'], 
    menu_icon="cast", default_index=0, orientation="horizontal")

app.run(selected)

#st.sidebar.title("Contribute")
#st.sidebar.info("This an open source project and you are very welcome to **contribute** your awesome comments,"
#                " questions, resources and groundwater models to the source code")
#st.sidebar.title("About")
#st.sidebar.info("This app is maintained and argued on by the GroMoPo mob")

# FIXME this should work independant of the system we are on. Make sure this works on all platforms including streamlit.io

if platform.system() == 'Windows':
    main_path = Path(".")
else:
    main_path = Path("streamlit")

#img_path = main_path.joinpath('pages','img','GroMoPo_logo_V1.png')
#st.sidebar.image(str(img_path), caption=None, width=None, use_column_width=None, clamp=False, channels='RGB', output_format='auto')
