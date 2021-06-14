# IMPORTS
import streamlit as st
import geopandas as gpd
import folium
from folium.features import GeoJsonPopup, GeoJsonTooltip
from folium import plugins
from folium.plugins import Fullscreen
from streamlit_folium import folium_static
from pathlib import Path
import platform
import os

# Configure for wide layout
st.set_page_config(layout="wide")

# Configure app layout and sidebar menu
st.sidebar.title('Navigation')

selection = st.sidebar.radio("Go to",['Home','Find Models','Submit Model','About'])

st.sidebar.title('Contribute')

st.sidebar.info("This an open source project and you are very welcome to **contribute** your awesome comments, questions, resources and groundwater models to the source code")

st.sidebar.title('About')

st.sidebar.info("This app is maintained and argued on by the GroMoPo mob")

if platform.system() == 'Darwin':
    image_path = 'GroMoPo_logo_V1.png'
else:
    image_path = os.getcwd() + '/streamlit/GroMoPo_logo_V1.png'

st.sidebar.image(image_path, caption=None, width=None, use_column_width=None, clamp=False, channels='RGB', output_format='auto')

# Configure multipage selector — reads .md files
def read_markdown_file(markdown_file):
    return Path(markdown_file).read_text()

if selection == 'Home':
    if platform.system() == 'Darwin':
        image_path = 'GroMoPo home banner.png'
        markdown = read_markdown_file('home_page.md')
    else:
        image_path = os.getcwd() + '/streamlit/GroMoPo home banner.png'
        markdown = read_markdown_file(os.getcwd() + '/streamlit/home_page.md')

    st.image(image_path, caption=None, width=None, use_column_width=None, clamp=False, channels='RGB', output_format='auto')
    st.markdown(markdown, unsafe_allow_html=True)

if selection == 'Submit Model':

    if platform.system() == 'Darwin':
        markdown = read_markdown_file('submit_page.md')
    else:
        markdown = read_markdown_file(os.getcwd() + '/streamlit/submit_page.md')

    st.markdown(markdown, unsafe_allow_html=True)

if selection == 'About':

    if platform.system() == 'Darwin':
        markdown = read_markdown_file('about_page.md')
    else:
        markdown = read_markdown_file(os.getcwd() + '/streamlit/about_page.md')

    st.markdown(markdown, unsafe_allow_html=True)

# Main app page — groundwater model display and search map
# NOTE: this could be refactored into a separate .py script and import on app start

if selection == 'Find Models':
    st.title('GroMoPo — Groundwater Model Portal')

    st.write("Sharing groundwater model data, knowledge and insights more easily through a portal of regional and global numerical groundwater models. The first priority is archiving existing models, but the repository could eventually archive model input and scripts for translating commonly used geospatial datasets into model inputs.")

    if platform.system() == 'Darwin':
        AUS_gdf_polygs = gpd.read_file('../QGIS/shapes/Australia.shp')
    else:
        AUS_gdf_polygs = gpd.read_file(os.getcwd() + '/QGIS/shapes/Australia.shp')

    AUS_gdf_polygs = AUS_gdf_polygs.to_crs(epsg='3857')
    AUS_gdf_points = AUS_gdf_polygs.copy()
    AUS_gdf_points["geometry"] = AUS_gdf_points["geometry"].centroid
    AUS_gdf_points = AUS_gdf_points.to_crs(epsg='4326')
    AUS_gdf_points['lon'] = AUS_gdf_points.geometry.x
    AUS_gdf_points['lat'] = AUS_gdf_points.geometry.y


    map = folium.Map(location=[-26, 135], zoom_start=3, crs='EPSG3857')

    folium.TileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', attr='x').add_to(map)
    folium.TileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', attr='x').add_to(map)

    marker_cluster = plugins.MarkerCluster().add_to(map)

    popup = GeoJsonPopup(
        fields=["Custodian", "Dev date", "Code"],
        aliases=["Custodian", "Dev date", "Code"],
        localize=True,
        labels=True,
        style="background-color: yellow;",
    )

    tooltip = GeoJsonTooltip(
        fields=["Custodian", "Dev date", "Code"],
        aliases=["Custodian", "Dev date", "Code"],
        localize=True,
        sticky=False,
        labels=True,
        style="""
            background-color: #F0EFEF;
            border: 2px solid black;
            border-radius: 3px;
            box-shadow: 3px;
        """,
        max_width=800,
    )


    for _, r in AUS_gdf_points.iterrows():
        folium.Marker(location=[r['lat'], r['lon']]).add_to(marker_cluster)

    g = folium.GeoJson(AUS_gdf_polygs, popup=popup, tooltip=tooltip, style_function = lambda feature: {
            'fillColor': 'grey',
            'weight': 1,
            'fillOpacity': 0.7,
    }).add_to(map)

    map.add_child(folium.LayerControl())

    Fullscreen().add_to(map)

    folium_static(map, height=700, width=1400)
