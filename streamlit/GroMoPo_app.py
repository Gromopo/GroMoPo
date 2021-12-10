import streamlit as st

# Our app libs - possibly move to own folder
from utils import helpers
from utils.multipage import MultiPage
from pages import home, about, submit_model

'''
This is the main app file that takes care of managing all subpages.
Logic about reading and displaying information is contained to each page.
'''

#st.set_page_config(layout="wide")

# Title of the main page
st.title("GroMoPoApp")

st.sidebar.title('Navigation')

app = MultiPage()
app.add_page("Home", home.app)
app.add_page("Submit Model", submit_model.app)
app.add_page("About", about.app)

app.run()

st.sidebar.title("Contribute")
st.sidebar.info("This an open source project and you are very welcome to **contribute** your awesome comments,"
                " questions, resources and groundwater models to the source code")
st.sidebar.title("About")
st.sidebar.info("This app is maintained and argued on by the GroMoPo mob")
st.sidebar.image('pages/img/GroMoPo_logo_V1.png', caption=None, width=None, use_column_width=None, clamp=False, channels='RGB', output_format='auto')
