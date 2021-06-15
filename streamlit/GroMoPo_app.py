# IMPORTS
import streamlit as st
import geopandas as gpd
# import matplotlib.cm as cm
# from matplotlib.pyplot import imread
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
    
    
    
#%% Load shapefiles in once before page loads

# Configure for wide layout
st.set_page_config(layout="wide")

if platform.system() == 'Darwin':
    logo_path = 'GroMoPo_logo_V1.png'
else:
    stdir = os.getcwd() # or provide path to \GroMoPo\streamlit\ folder
    logo_path = os.path.join(stdir,'GroMoPo_logo_V1.png')
    if not os.path.isfile(logo_path):
        # Add streamlit for web
        stdir = os.path.join(os.getcwd(),'streamlit')
        logo_path = os.path.join(stdir,'GroMoPo_logo_V1.png')

epsg = 3857# mercator default 
# Load each continent and concatenate - might make more sense to load only one global shp in
continents = ['africa','oceania','asia','europe','north_america','south_america']
shp_dir = os.path.join('data','shapes')

all_gdfs = []
for continent in continents:
    if platform.system() == 'Darwin':
        shp_dir2 = os.path.join('..',shp_dir)
        shp_fname = os.path.join('..',shp_dir,'{}.shp'.format(continent))
        # AUS_gdf_polygs = gpd.read_file('../QGIS/shapes/Australia.shp')
        # NA_gdf_polygs = gpd.read_file('../QGIS/shapes/north_america.shp')
    else:
        shp_dir2 = os.path.join(os.path.dirname(stdir),shp_dir)
        shp_fname = os.path.join(os.path.dirname(stdir),shp_dir,'{}.shp'.format(continent))
        # AUS_gdf_polygs = gpd.read_file(os.getcwd() + '/QGIS/shapes/Australia.shp')
        # NA_gdf_polygs = gpd.read_file(os.getcwd() + '/QGIS/shapes/north_america.shp')
#     if os.path.isfile(shp_fname):
#         temp_df=gpd.read_file(shp_fname)
#         if temp_df.crs.to_epsg() != epsg:
#             temp_df.to_crs(epsg=epsg,inplace=True)
#         all_gdfs.append(temp_df)

# all_gdf = gpd.GeoDataFrame(gpd.pd.concat(all_gdfs)) # one shp to plot, requires consistent attributes
# if all_gdf.crs.to_epsg() != epsg: # convert crs, if needed
#     all_gdf.to_crs(epsg=epsg,inplace=True)

#%%






# Configure app layout and sidebar menu
st.sidebar.title('Navigation')

selection = st.sidebar.radio("Go to",['Home','Find Models','Submit Model','About'])
# selection='Find Models'
st.sidebar.title('Contribute')

st.sidebar.info("This an open source project and you are very welcome to **contribute** your awesome comments, questions, resources and groundwater models to the source code")

st.sidebar.title('About')

st.sidebar.info("This app is maintained and argued on by the GroMoPo mob")

st.sidebar.info("{}".format(os.path.isdir(shp_dir2)))
st.sidebar.info("{}".format(shp_dir2))

st.sidebar.info("{}".format(os.path.isfile(logo_path)))
st.sidebar.info("{}".format(logo_path))
        
# st.sidebar.image(logo_path, caption=None, width=None, use_column_width=None, clamp=False, channels='RGB', output_format='auto')

# if selection == 'Home':
#     if platform.system() == 'Darwin':
#         image_path = 'GroMoPo home banner.png'
#         markdown = read_markdown_file('home_page.md')
#     else:
#         image_path = os.path.join(stdir,'GroMoPo home banner.png')
#         markdown = read_markdown_file(os.path.join(stdir,'home_page.md'))

#     st.image(image_path, caption=None, width=None, use_column_width=None, clamp=False, channels='RGB', output_format='auto')
#     st.markdown(markdown, unsafe_allow_html=True)

# if selection == 'Submit Model':

#     if platform.system() == 'Darwin':
#         markdown = read_markdown_file('submit_page.md')
#     else:
#         markdown = read_markdown_file(os.path.join(stdir,'submit_page.md'))

#     st.markdown(markdown, unsafe_allow_html=True)

#     #components.iframe("https://docs.google.com/forms/d/e/1FAIpQLSeOgQtYLJALacZQfwF2Nb5RMWOqg_ODVyyEXoStBKHekfg66w/viewform?usp=sf_link", height=1500, scrolling=True)

# if selection == 'About':

#     if platform.system() == 'Darwin':
#         markdown = read_markdown_file('about_page.md')
#     else:
#         markdown = read_markdown_file(os.path.join(stdir,'about_page.md'))

#     st.markdown(markdown, unsafe_allow_html=True)

# # Main app page — groundwater model display and search map
# # NOTE: this could be refactored into a separate .py script and import on app start

# if selection == 'Find Models':
#     st.title('GroMoPo — Groundwater Model Portal')

#     st.write("Sharing groundwater model data, knowledge and insights more easily through a portal of regional and global numerical groundwater models. The first priority is archiving existing models, but the repository could eventually archive model input and scripts for translating commonly used geospatial datasets into model inputs.")
    
    

#     map = folium.Map(zoom_start=3, crs='EPSG{}'.format(epsg),min_zoom=3,max_bounds=True)

#     folium.TileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', attr='x',name='OpenTopoMap').add_to(map)
#     folium.TileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',name='ArcWorldImagery', attr='x').add_to(map)
    
#     rast_fname = os.path.join(os.path.dirname(os.path.dirname(shp_fname)),'degraaf_gw_dep.png')
#     st.sidebar.info('{}'.format(os.path.isfile(rast_fname)))
#     # img = imread(rast_fname)
#     # I can't find a way to load a tif in...could save as txt or similar but would be a big file. TBD
#     # img = load_rast(rast_fname) # 36 MB, not sure effect on load time from github
#     # img = gdal.Open(rast_fname).ReadAsArray()
        
#     # cm_out = cmap(img)
#     # skip_rows=60
#     # cm_out = img[skip_rows:-skip_rows,:,:]
    
#     # rgroup = folium.FeatureGroup(name='Water table depth [de Graaf] (Yellow = >100 m | Blue = <=0 m)').add_to(map)
#     # rgroup.add_child(folium.raster_layers.ImageOverlay(cm_out,opacity=0.6,bounds=[[-90,-180],[90,180]],mercator_project=True))#.add_to(map) #
    
    
    
#     marker_cluster = plugins.MarkerCluster(control=False).add_to(map)

#     # popup_AU = GeoJsonPopup(
#     #     fields=["Custodian", "Dev date", "Code"],
#     #     aliases=["Custodian", "Dev date", "Code"],
#     #     localize=True,
#     #     labels=True,
#     #     style="background-color: yellow;",
#     # )

#     # tooltip_AU = GeoJsonTooltip(
#     #     fields=["Custodian", "Dev date", "Code"],
#     #     aliases=["Custodian", "Dev date", "Code"],
#     #     localize=True,
#     #     sticky=False,
#     #     labels=True,
#     #     style="""
#     #         background-color: #F0EFEF;
#     #         border: 2px solid black;
#     #         border-radius: 3px;
#     #         box-shadow: 3px;
#     #     """,
#     #     max_width=800,
#     # )

#     popup_NA = GeoJsonPopup(
#             fields=["id", "devdate", "name", "url", "custodian", "spscale", "purpose", "archive", "coupling", "contribu_1"],
#             aliases=["ID", "Date Developed", "Name", "URL", "Custodian", "Spatial Scale", "Purpose", "Archive", "Coupling", "Contributed by"],
#             localize=True,
#             labels=True,
#             style="background-color: yellow;",
#         )

#     # for _, r in all_gdf.to_crs(epsg='4326').iterrows():
#     #     folium.Marker(location=[r.geometry.centroid.y, r.geometry.centroid.x]).add_to(marker_cluster)

#     # h = folium.GeoJson(all_gdf,name='Groundwater models', popup=popup_NA, style_function = lambda feature: {
#     #             'fillColor': 'grey',
#     #             'weight': 1,
#     #             'fillOpacity': 0.7,
#     # }).add_to(map)




#     # for _, r in AUS_gdf_points.iterrows():
#     #     folium.Marker(location=[r['lat'], r['lon']]).add_to(marker_cluster)

#     # for _, r in NA_gdf_points.iterrows():
#     #     folium.Marker(location=[r['lat'], r['lon']]).add_to(marker_cluster)

#     # g = folium.GeoJson(AUS_gdf_polygs, popup=popup_AU, tooltip=tooltip_AU, style_function = lambda feature: {
#     #         'fillColor': 'grey',
#     #         'weight': 1,
#     #         'fillOpacity': 0.7,
#     # }).add_to(map)

#     # h = folium.GeoJson(NA_gdf_polygs, popup=popup_NA, style_function = lambda feature: {
#     #             'fillColor': 'grey',
#     #             'weight': 1,
#     #             'fillOpacity': 0.7,
#     # }).add_to(map)

#     map.add_child(folium.LayerControl())
#     # if epsg == 3857:
#     #     map.setMaxBounds([[-20026376.39, -20048966.10],
#     #                       [20026376.39, 20048966.10]]) # if EPSG=3857 # Pseudo-Mercator
#     # elif epsg == 4326:
#     #     map.setMaxBounds([[-180,-85.06],[180,85.06]]) # if EPSG=4326 # WGS84

#     Fullscreen().add_to(map)

#     folium_static(map, height=700, width=1400)
    
#     # map.save('test.html')
