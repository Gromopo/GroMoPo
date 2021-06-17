# IMPORTS
import streamlit as st
import geopandas as gpd
# import matplotlib.cm as cm
from matplotlib.pyplot import imread
# import numpy as np
import folium
from folium.features import GeoJsonPopup, GeoJsonTooltip
from folium import plugins
from folium.plugins import Fullscreen
from streamlit_folium import folium_static
import streamlit.components.v1 as components
from pathlib import Path
import platform
import os

#%% Supporting functions - eventually create function library?

# Configure multipage selector — reads .md files
def read_markdown_file(markdown_file):
    return Path(markdown_file).read_text()

# def load_rast(fname,band=0):
#     with rio.open(fname) as src:
#         img = src.read()[band]
#         # bounds = src.bounds[:]
#         # bounds = [[bounds[1],bounds[0]],[bounds[3],bounds[2]]]
#     return img

# def cmap(img,cmap='viridis',nan_val=None,vminmax=[0,100]):
#     if nan_val is None:
#         # Assume lowest value is nan value to skip in colormap
#         nan_val = img.min()
    
#     img2 = img.copy()
#     img2[img2==nan_val] = np.nan
#     cmap_obj = cm.get_cmap(cmap)
#     if vminmax[0] is None:
#         norm_data =(img2 - np.nanmin(img2))/(np.nanmax(img2)-np.nanmin(img2))
#     else:
#         norm_data = (img2-vminmax[0])/(vminmax[1]-vminmax[0])
#     cm_out = cmap_obj(norm_data)
#     cm_out[np.isnan(img2),:] = 1
#     return cm_out

popup = GeoJsonPopup(
            fields=["id", "devdate", "name", "url", "custodian", "spscale", "purpose", "archive", "coupling", "contribu_1"],
            aliases=["ID", "Date Developed", "Name", "URL", "Custodian", "Spatial Scale", "Purpose", "Archive", "Coupling", "Contributed by"],
            localize=True,
            labels=True,
            style="background-color: yellow;",
        )
    
    
    
# This and all map related commands would be nice to cache, but not easy: https://github.com/randyzwitch/streamlit-folium/issues/4
def plot_map(gdf,img,popup=None):
    
    rgroup = folium.FeatureGroup(name='Water table depth [de Graaf] (Yellow = >100 m | Blue = <=0 m)')
    rgroup.add_child(folium.raster_layers.ImageOverlay(img,opacity=0.6,bounds=[[-90,-180],[90,180]],mercator_project=True))
    
    marker_cluster = plugins.MarkerCluster(control=False)
    
    for _, r in gdf.to_crs(epsg='4326').iterrows():
        folium.Marker(location=[r.geometry.centroid.y, r.geometry.centroid.x]).add_to(marker_cluster)

    mlayer=folium.GeoJson(gdf,name='Groundwater models', popup=popup, style_function = lambda feature: {
                'fillColor': 'grey',
                'weight': 1,
                'fillOpacity': 0.7,
    })
    return rgroup, marker_cluster, mlayer
    

    
    
    
@st.cache    
def load_shp(dirname,continents = ['africa','oceania','asia','europe','north_america','south_america'],
             epsg = 3857, shp_dir=os.path.join('data','shapes')):
    all_gdfs = []
    for continent in continents:
        if platform.system() == 'Darwin':
            shp_dir2 = os.path.join('..',shp_dir)
            shp_fname = os.path.join('..',shp_dir,'{}.shp'.format(continent))
            # AUS_gdf_polygs = gpd.read_file('../QGIS/shapes/Australia.shp')
            # NA_gdf_polygs = gpd.read_file('../QGIS/shapes/north_america.shp')
        else:
            shp_dir2 = os.path.join(os.path.dirname(dirname),shp_dir)
            shp_fname = os.path.join(os.path.dirname(dirname),shp_dir,'{}.shp'.format(continent))
            # AUS_gdf_polygs = gpd.read_file(os.getcwd() + '/QGIS/shapes/Australia.shp')
            # NA_gdf_polygs = gpd.read_file(os.getcwd() + '/QGIS/shapes/north_america.shp')
        if os.path.isfile(shp_fname):
            temp_df=gpd.read_file(shp_fname)
            if temp_df.crs.to_epsg() != epsg:
                temp_df.to_crs(epsg=epsg,inplace=True)
            all_gdfs.append(temp_df)
    
    all_gdf = gpd.GeoDataFrame(gpd.pd.concat(all_gdfs)) # one shp to plot, requires consistent attributes
    if all_gdf.crs.to_epsg() != epsg: # convert crs, if needed
        all_gdf.to_crs(epsg=epsg,inplace=True)
    
    return all_gdf,shp_dir2

@st.cache  
def read_img(fname,skip_rows=60):
    img = imread(fname)
    
    cm_out = img[skip_rows:-skip_rows,:,:]
    return cm_out
        
#%% Load shapefiles in once

# Configure for wide layout
st.set_page_config(layout="wide")

if platform.system() == 'Darwin':
    logo_path = 'GroMoPo_logo_V1.png'
else:
    stdir = os.getcwd() # or provide path to \GroMoPo\streamlit\ folder
    logo_path = os.path.join(stdir,'GroMoPo_logo_V1.png')
    if not os.path.isfile(logo_path):
        # Add streamlit for web
        stdir = os.path.join(stdir,'streamlit')
        logo_path = os.path.join(stdir,'GroMoPo_logo_V1.png')

epsg = 3857
# Load shapefiles of models
all_gdf,shp_dir = load_shp(stdir,epsg=epsg)

# Load water table base map
rast_fname = os.path.join(os.path.dirname(shp_dir),'degraaf_gw_dep.png')
img = read_img(rast_fname)



#%% App
# Configure app layout and sidebar menu
st.sidebar.title('Navigation')

selection = st.sidebar.radio("Go to",['Home','Find Models','Submit Model','About'])
# selection='Find Models'
st.sidebar.title('Contribute')

st.sidebar.info("This an open source project and you are very welcome to **contribute** your awesome comments, questions, resources and groundwater models to the source code")

st.sidebar.title('About')

st.sidebar.info("This app is maintained and argued on by the GroMoPo mob")


st.sidebar.image(logo_path, caption=None, width=None, use_column_width=None, clamp=False, channels='RGB', output_format='auto')

if selection == 'Home':
    if platform.system() == 'Darwin':
        image_path = 'GroMoPo home banner.png'
        markdown = read_markdown_file('home_page.md')
    else:
        image_path = os.path.join(stdir,'GroMoPo home banner.png')
        markdown = read_markdown_file(os.path.join(stdir,'home_page.md'))

    st.image(image_path, caption=None, width=None, use_column_width=None, clamp=False, channels='RGB', output_format='auto')
    st.markdown(markdown, unsafe_allow_html=True)

if selection == 'Submit Model':

    if platform.system() == 'Darwin':
        markdown = read_markdown_file('submit_page.md')
    else:
        markdown = read_markdown_file(os.path.join(stdir,'submit_page.md'))

    st.markdown(markdown, unsafe_allow_html=True)

    #components.iframe("https://docs.google.com/forms/d/e/1FAIpQLSeOgQtYLJALacZQfwF2Nb5RMWOqg_ODVyyEXoStBKHekfg66w/viewform?usp=sf_link", height=1500, scrolling=True)

if selection == 'About':

    if platform.system() == 'Darwin':
        markdown = read_markdown_file('about_page.md')
    else:
        markdown = read_markdown_file(os.path.join(stdir,'about_page.md'))

    st.markdown(markdown, unsafe_allow_html=True)

# Main app page — groundwater model display and search map
# NOTE: this could be refactored into a separate .py script and import on app start

if selection == 'Find Models':
    st.title('GroMoPo — Groundwater Model Portal')

    st.write("Sharing groundwater model data, knowledge and insights more easily through a portal of regional and global numerical groundwater models. The first priority is archiving existing models, but the repository could eventually archive model input and scripts for translating commonly used geospatial datasets into model inputs.")
    
    map = folium.Map(zoom_start=3, crs='EPSG{}'.format(epsg),min_zoom=3,max_bounds=True)
    folium.TileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', attr='x',name='OpenTopoMap').add_to(map)
    folium.TileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',name='ArcWorldImagery', attr='x').add_to(map)
    
    
    rgroup, marker_cluster, mlayer = plot_map(all_gdf,img,popup=popup)
    
    rgroup.add_to(map)
    marker_cluster.add_to(map)
    mlayer.add_to(map)
    
    map.add_child(folium.LayerControl())

    Fullscreen().add_to(map)
    
    folium_static(map, height=700, width=1400)
    
