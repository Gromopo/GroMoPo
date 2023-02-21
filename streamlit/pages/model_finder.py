import streamlit as st
import folium
from folium.features import GeoJsonPopup
from streamlit_folium import folium_static
from matplotlib.pyplot import imread
from pathlib import Path
import platform

# Are we running on streamlit.io?
if platform.system() == 'Windows':
    main_path = Path("..")
else:
    main_path = Path(".")

@st.cache
def read_img(fname, skip_rows=60):
    img = imread(fname)
    cm_out = img[skip_rows:-skip_rows, :, :]
    return cm_out


def plot_rasters(rasters, to_epsg='4326'):
    
    # loop through rasters
    rgroups = []
    for img in rasters:
    
        rgroup = folium.FeatureGroup(name=rasters[img]['name'],overlay=True)
        rgroup.add_child(folium.raster_layers.ImageOverlay(rasters[img]['data'], opacity=0.6,
                                                           bounds=[[-90, -180], [90, 180]],
                                                           mercator_project=True))
        rgroups.append(rgroup)
        
    return rgroups


def popup_html(df):
    
    title = df['name']
    abstract = df['abstract']
    url = df['url']
    authors = df['authors']
    
    try:
        strAuthors = ", ".join(authors)

    except:
        strAuthors = "Not available"
        
    html = """
    <!DOCTYPE html>
<html>
<strong>""" + title + """</strong><br>
<a href='""" + url + """'>View Resource in HydroShare</a><br>
Authors: """ + strAuthors + """<br>
Abstract: """ + abstract + """
</html>
"""
    return html
    

def app():
    st.title('GroMoPo — Groundwater Model Portal')
    st.write("Sharing groundwater model data, knowledge and insights more easily through"
             " a portal of regional and global numerical groundwater models. "
             "The first priority is archiving existing models, but the repository could eventually archive"
             " model input and scripts for translating commonly used geospatial datasets into model inputs.")

    # st.write("Path: {}".format(rast_fname))
    
    # set coordinate reference system
    epsg = 3857
    
    # create map
    m = folium.Map(zoom_start=3, crs='EPSG{}'.format(epsg), min_zoom=3, max_bounds=True)
    
    # add 
    folium.TileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', attr='x', name='OpenTopoMap').add_to(m)
    folium.TileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                     name='ArcWorldImagery', attr='x').add_to(m)
    
    
    # set up raster
    rast_fname = str(main_path.absolute().joinpath('data', 'degraaf_gw_dep.png'))
    img = read_img(rast_fname)
    rasters_dict = {'degraaf_dep': {'name': 'Water table depth [de Graaf] (Yellow = >100 m | Blue = <=0 m)',
                                    'data': img}}
    
    # prep rasters
    rgroups = plot_rasters(rasters_dict)
    
    # Add raster data to map
    for rgroup in rgroups:
        rgroup.add_to(m)
    
    # load geojson
    modelsURL = 'https://maps.kgs.ku.edu/GroMoPo/GroMoPo_MapData.json'
    
    # set up vector popup
    popup = GeoJsonPopup(
        fields=["name", "abstract", "authors", "url"],
        aliases=["Title", "Abstract", "Authors", "URL"]
    )
    
    # html = popup_html(i)
    # popup = folium.Popup(html, parse_html=True, max_width=500)
    
    # add vector data to the map
    folium.GeoJson(modelsURL, name='Groundwater models', popup=popup).add_to(m)

    folium_static(m, height=700, width=1400)
