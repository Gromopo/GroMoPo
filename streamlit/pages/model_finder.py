import streamlit as st
import folium
from folium.features import GeoJsonPopup, GeoJsonTooltip
from folium import plugins
from folium.plugins import Fullscreen
from streamlit_folium import folium_static
import geopandas as gpd
from matplotlib.pyplot import imread
from pathlib import Path

from utils import helpers as hp

# This and all map related commands would be nice to cache, but not easy:
# https://github.com/randyzwitch/streamlit-folium/issues/4
def plot_map(gdf, img, popup=None):
    rgroup = folium.FeatureGroup(name='Water table depth [de Graaf] (Yellow = >100 m | Blue = <=0 m)')
    rgroup.add_child(folium.raster_layers.ImageOverlay(img, opacity=0.6, bounds=[[-90, -180], [90, 180]],
                                                       mercator_project=True))
    
    marker_cluster = plugins.MarkerCluster(control=False)
    
    for _, r in gdf.to_crs(epsg='4326').iterrows():
        folium.Marker(location=[r.geometry.centroid.y, r.geometry.centroid.x]).add_to(marker_cluster)

    mlayer=folium.GeoJson(gdf, name='Groundwater models', popup=popup, style_function = lambda feature: {
                'fillColor': 'grey',
                'weight': 1,
                'fillOpacity': 0.7,
    })
    return rgroup, marker_cluster, mlayer    


@st.cache(suppress_st_warning=True)
def load_shp(dirname, continents=['africa', 'oceania', 'asia', 'europe', 'north_america', 'south_america'],
             epsg=3857):
    all_gdfs = []
    shp_dir = Path(dirname).parent.joinpath('data', 'shapes')
    for continent in continents:
        shp_fname = shp_dir.joinpath('{}.shp'.format(continent))
        # AUS_gdf_polygs = gpd.read_file('../QGIS/shapes/Australia.shp')
        # NA_gdf_polygs = gpd.read_file('../QGIS/shapes/north_america.shp')
        if shp_fname.exists():
            temp_df = gpd.read_file(shp_fname)
            if temp_df.crs.to_epsg() != epsg:
                temp_df.to_crs(epsg=epsg, inplace=True)
            all_gdfs.append(temp_df)

    if not all_gdfs:
        # Somehow the list is empty and something went wrong
        st.error("No model data to display from path {}".format(shp_dir))
        return
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
all_gdf, shp_dir = load_shp("..", epsg=epsg) #Path().absolute()
print(Path().absolute())
# Load water table base map
rast_fname = Path("..").joinpath('data', 'degraaf_gw_dep.png')#Path().absolute().parent.joinpath('data', 'degraaf_gw_dep.png')
img = read_img(rast_fname)


def app():
    st.title('GroMoPo — Groundwater Model Portal')
    st.write("Sharing groundwater model data, knowledge and insights more easily through"
             " a portal of regional and global numerical groundwater models."
             "The first priority is archiving existing models, but the repository could eventually archive"
             " model input and scripts for translating commonly used geospatial datasets into model inputs.")
    
    st.write("Path: {}".format(Path().absolute()))
    
    map = folium.Map(zoom_start=3, crs='EPSG{}'.format(epsg), min_zoom=3, max_bounds=True)
    folium.TileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', attr='x',name='OpenTopoMap').add_to(map)
    folium.TileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                     name='ArcWorldImagery', attr='x').add_to(map)
    rgroup, marker_cluster, mlayer = plot_map(all_gdf, img, popup=popup)

    rgroup.add_to(map)
    marker_cluster.add_to(map)
    mlayer.add_to(map)

    map.add_child(folium.LayerControl())

    Fullscreen().add_to(map)

    folium_static(map, height=700, width=1400)
    
