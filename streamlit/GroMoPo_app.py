import streamlit as st

# Our app libs - possibly move to own folder
# from utils import helpers
from utils.multipage import MultiPage
from pages import home, about, submit_model, model_finder
from pathlib import Path
import platform

#st.set_page_config(layout="wide")

st.sidebar.title('Navigation')

app = MultiPage()
app.add_page("Home", home.app) # Name, Function
app.add_page("Model Finder", model_finder.app)
app.add_page("Submit Model", submit_model.app)
app.add_page("About", about.app)

app.run()

st.sidebar.title("Contribute")
st.sidebar.info("This an open source project and you are very welcome to **contribute** your awesome comments,"
                " questions, resources and groundwater models to the source code")
st.sidebar.title("About")
st.sidebar.info("This app is maintained and argued on by the GroMoPo mob")

if platform.system() == 'Darwin':
    main_path = Path("streamlit")
else:
    main_path = Path(".")

img_path = main_path.joinpath('pages','img','GroMoPo_logo_V1.png')
st.sidebar.image(str(img_path), caption=None, width=None, use_column_width=None, clamp=False, channels='RGB', output_format='auto')
