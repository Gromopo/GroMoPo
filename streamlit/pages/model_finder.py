import streamlit as st
import folium
from folium.features import GeoJsonPopup, GeoJsonTooltip
from folium import plugins
from folium.plugins import Fullscreen
from streamlit_folium import folium_static
import geopandas as gpd
from matplotlib.pyplot import imread
from pathlib import Path
import platform

from utils import helpers as hp

# This and all map related commands would be nice to cache, but not easy:
# https://github.com/randyzwitch/streamlit-folium/issues/4
def plot_map(shp_df, rasters=None, popup=None,to_epsg='4326'):
    
    
    rgroups = []
    for img in rasters:
    
        rgroup = folium.FeatureGroup(name=rasters[img]['name'],overlay=True)
        rgroup.add_child(folium.raster_layers.ImageOverlay(rasters[img]['data'], opacity=0.6,
                                                           bounds=[[-90, -180], [90, 180]],
                                                           mercator_project=True))
        rgroups.append(rgroup)
    
    marker_cluster = plugins.MarkerCluster(control=False)
    # Domains with detailed spatial extents
    for _, r in shp_df.to_crs(epsg=to_epsg).iterrows():
        folium.Marker(location=[r.geometry.centroid.y, r.geometry.centroid.x]).add_to(marker_cluster)

    mlayer=folium.GeoJson(shp_df, name='Groundwater models', popup=popup,
                          style_function = lambda feature: {
                            'fillColor': 'grey',
                            'color':feature['properties']['color'],
                            'weight': 1,
                            'fillOpacity': 0.7,
    })
    
    mlayers.append(mlayer)
        
    
    
    return rgroups, marker_cluster, mlayer   


@st.cache(suppress_st_warning=True)
def load_shp(dirname, shpnames=['wdomain','woutdomain'],
             epsg=3857,color_dict={'wdomain':'blue',
                                   'woutdomain':'red',
                                   'other':'green'}):
    all_gdfs = []
    shp_dir = Path(dirname).joinpath('data', 'shapes')
    for shpname in shpnames:
        shp_fname = shp_dir.joinpath('{}.shp'.format(shpname))
        # AUS_gdf_polygs = gpd.read_file('../QGIS/shapes/Australia.shp')
        # NA_gdf_polygs = gpd.read_file('../QGIS/shapes/north_america.shp')
        if shp_fname.exists():
            temp_df = gpd.read_file(shp_fname)
            if temp_df.crs.to_epsg() != epsg:
                temp_df.to_crs(epsg=epsg, inplace=True)
            
            if shpname in color_dict:
                temp_df['color'] = color_dict[shpname]
            else:
                temp_df['color'] = color_dict['other']
            
            all_gdfs.append(temp_df)

    if not all_gdfs:
        # Somehow the list is empty and something went wrong
        st.error("No model data to display from path {}".format(shp_dir))
        st.error("Path: {}".format(Path().absolute()))
        return None,None
    all_gdf = gpd.GeoDataFrame(gpd.pd.concat(all_gdfs))
    # one shp to plot, requires consistent attributes
    if all_gdf.crs is None:
        all_gdf.set_crs(epsg, allow_override=True, inplace=True)
    # if all_gdf.crs.to_epsg() != epsg:
    #     # convert crs, if needed
    #     all_gdf.to_crs(epsg=epsg, inplace=True)
    
    return all_gdf, shp_dir

@st.cache  
def read_img(fname, skip_rows=60):
    img = imread(fname)
    cm_out = img[skip_rows:-skip_rows, :, :]
    return cm_out


if platform.system() == 'Windows':
    main_path = Path("..")
else:
    main_path = Path(".")

popup = GeoJsonPopup(
            fields=["id", "devdate", "name", "url", "custodian",
                    "spscale", "purpose", "archive", "coupling", "contribu_1"],
            aliases=["ID", "Date Developed", "Name", "URL", "Custodian", "Spatial Scale",
                     "Purpose", "Archive", "Coupling", "Contributed by"],
            localize=True,
            labels=True,
            style="background-color: yellow;",
        )

epsg = 3857
# Load shapefiles of models
all_gdf, shp_dir = load_shp(main_path, epsg=epsg) #Path().absolute()
# print(Path().absolute())
#Load water table base map
rast_fname = str(main_path.absolute().joinpath('data', 'degraaf_gw_dep.png'))
img = read_img(rast_fname)
rasters_dict = {'degraaf_dep':{'name':'Water table depth [de Graaf] (Yellow = >100 m | Blue = <=0 m)',
                               'data':img}}


def app():
    st.title('GroMoPo — Groundwater Model Portal')
    st.write("Sharing groundwater model data, knowledge and insights more easily through"
             " a portal of regional and global numerical groundwater models."
             "The first priority is archiving existing models, but the repository could eventually archive"
             " model input and scripts for translating commonly used geospatial datasets into model inputs.")
    
    # st.write("Path: {}".format(rast_fname))
    
    m = folium.Map(zoom_start=3, crs='EPSG{}'.format(epsg), min_zoom=3, max_bounds=True)
    folium.TileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', attr='x',name='OpenTopoMap').add_to(m)
    folium.TileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                     name='ArcWorldImagery', attr='x').add_to(m)
    rgroups, marker_cluster, mlayer = plot_map(all_gdf,
                                              rasters=rasters_dict,
                                              popup=popup)
    # Add raster data to map
    for rgroup in rgroups:
        rgroup.add_to(m)
        
    # Add clusters
    modelgroup1 = folium.FeatureGroup(name="Model domains").add_to(m)
    modelgroup1.add_child(marker_cluster)
    modelgroup1.add_child(mlayer)
    
    m.add_child(modelgroup1)
    m.add_child(folium.LayerControl())
    Fullscreen().add_to(m)

    folium_static(m, height=700, width=1400)
    
