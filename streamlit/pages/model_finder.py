from collections import OrderedDict
import streamlit as st
import folium
from folium.features import GeoJsonPopup#, GeoJsonTooltip
from folium import plugins
from folium.plugins import Fullscreen
from streamlit_folium import folium_static
import geopandas as gpd
from matplotlib.pyplot import imread
from pathlib import Path
import platform

#from utils import helpers as hp

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
    mlayers = []
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


popup_dict = OrderedDict({"id":"ID", "devdate":"Date developed", "name":"Model name",
              "url":"Publication link(s)", "custodian":"Authors",
                    "spscale":"Spatial scale", "purpose":"Purpose", "archive":"Model link(s)",
                    "coupling":"Coupling", "contribu_1":"Contributed by"})

@st.cache  
def popupHTML(row, popup_dict=popup_dict,col1width=50):
    '''Create custom HTML for popup.

    Parameters
    ----------
    row : TYPE
        DESCRIPTION.

    Returns
    -------
    html : TYPE
        DESCRIPTION.
        
    After: https://towardsdatascience.com/folium-map-how-to-create-a-table-style-pop-up-with-html-code-76903706b88a

    '''
    html = """<!DOCTYPE html>
            <html>
            
            <table>
            <tbody>
            """
    
    for key, value in popup_dict.items():
        # Loop through entries for popup with specific formatting
        
        if row[key] is None:
            second_col_val= 'N/A'
        else:
            second_col_val = row[key]
        
        if 'link' in value: # format for clickable link
            html += """<tr>
                       <td><span style="width: {0}px; color: #293191; overflow-wrap: break-word;"><b>{1}</b></span></td>
                       <td><span style="overflow-wrap: break-word;>""".format(col1width,value) # Attribute name
                       
            # if second_col_val != 'N/A' and second_col_val is not None:
                
            links = second_col_val.split('|')
            links.insert(0,"") # for some reason need a dummy entry, as first entry doesn't show up as link, only as text.
            
                
            # link_html = """ """.join(["""<a href="{0}" target="_blank"> {0}</a><br>""".format(link) for link in links])
            link_html = """ """
            for i,link in enumerate(links):
                if i == 0:
                    link_html += """<a href="{0}" target="_blank">{0}</a>""".format(link)
                elif link == 'N/A':
                    link_html += """{}<br>""".format(link)
                else:
                    link_html += """<a href="{0}" target="_blank">{0}</a><br>""".format(link)
            
            html += link_html
            # else:
            #     html += """{0}<br>""".format(second_col_val)
                
            html += """</span></td></tr>"""
            # html += """</td></td></td></tr>"""


        else:
            html += """<tr>
                       <td><span style="width: {0}px;color: #000000;overflow-wrap: break-word;"><b>{1}</b></span></td>
                       <td style="overflow-wrap: break-word;">{2}</td></tr>""".format(col1width,value,second_col_val)
                       
    
    html += """</tbody>
               </table>                    
               </html>"""
    
    return html

# popup = GeoJsonPopup(
#             fields=["id", "devdate", "name", "url", "custodian",
#                     "spscale", "purpose", "archive", "coupling", "contribu_1"],
#             aliases=["ID", "Date Developed", "Name", "URL", "Custodian", "Spatial Scale",
#                      "Purpose", "Archive", "Coupling", "Contributed by"],
#             localize=True,
#             labels=True,
#             style="background-color: yellow;overflow-wrap: break-word;",
#         )
popup = GeoJsonPopup(labels=False,fields=["popup_html"],
                     localize=True,style="background-color: blue;overflow-wrap: break-word;")

epsg = 3857
# Load shapefiles of models
all_gdf, shp_dir = load_shp(main_path, epsg=epsg) #Path().absolute()
# Replace None values as "N/A"
objc = list(all_gdf.select_dtypes(include=['object']).columns.values)
all_gdf[objc] = all_gdf[objc].replace([None],'N/A')

# Create popup html attribute
all_gdf['popup_html'] = all_gdf.apply(popupHTML,axis=1)

# print(Path().absolute())
#Load water table base map
rast_fname = str(main_path.absolute().joinpath('data', 'degraaf_gw_dep.png'))
img = read_img(rast_fname)
rasters_dict = {'degraaf_dep':{'name':'Water table depth [de Graaf] (Yellow = >100 m | Blue = <=0 m)',
                               'data':img}}

# pt_fname = str(main_path.absolute().joinpath('data', 'sprint_11_2021_plot.csv'))
# ptsq_df = csv2shp(pt_fname,crs=epsg)

# Can merge, but better to keep separate
# all_gdf = gpd.GeoDataFrame(gpd.pd.concat([all_gdf,ptsq_df],ignore_index=True))
# all_gdf.set_crs(epsg, allow_override=True, inplace=True)

# Separate datasets for models with and without domain shps

# shp_dict = {'wdomains':all_gdf,
#             'woutdomains':ptsq_df,
#             }


def app():
    st.title('GroMoPo ??? Groundwater Model Portal')
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
    # marker_cluster.add_to(m)
    
    modelgroup1 = folium.FeatureGroup(name="Model domains").add_to(m)
    modelgroup1.add_child(marker_cluster)
    modelgroup1.add_child(mlayer)
    
    # for mg,mlayer in zip([modelgroup1,modelgroup2],mlayers):
    #     mg.add_child(mlayer).add_to(m)
    # # Add shps to map - looping didn't work for some reason?
    # modelgroup.add_child(mlayers[0])
    
    # modelgroup2 = folium.FeatureGroup(name="Approximate domains")
    # modelgroup2.add_child(mlayers[1])    
    
    # for ishp in mlayers:
    #     ishp.add_to(map)
    
    # modelgroup.add_to(map)
    # modelgroup1.add_to(m)
    # modelgroup2.add_to(m)
    
    # folium.LayerControl().add_to(m)
    m.add_child(modelgroup1)
    # m.add_child(modelgroup2)
    m.add_child(folium.LayerControl())
    Fullscreen().add_to(m)

    folium_static(m, height=700, width=1400)
       
