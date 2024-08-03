import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
from streamlit_folium import st_folium
from pyproj import CRS

st.set_page_config(page_title='UBCV Class Map', page_icon=':bar_chart:', layout='wide')

st.title('My First App - Hello World :)')
st.write("I'm going to make a map of the campus and put my classes on it")

st.divider()

st.header('All My UBC Courses')
gclss = gpd.read_file("geo_files/geoclass1.geojson")
gc = pd.DataFrame(gclss)
gc1 = gc.drop('geometry', axis=1)
gc2 = gc1[["Section", "Instructional Format", "Days", "Start", "End", "Room", "Building", "SHORTNAME", "NAME"]]
st.dataframe(gc2)

st.divider()

def calculate_distance(row, dest_geom, src_col='geometry'):
    # Calculate the distances (in meters)
    dist = row[src_col].distance(dest_geom)

    # Convert into kilometers
    dist_km = dist / 1000

    # Assign the distance to the original data
    #row[target_col] = dist_km
    return dist_km

bcen = gpd.read_file("geo_files/ubc_buildings_centroids.geojson")
bcen['lon'] = bcen.geometry.x
bcen['lat'] = bcen.geometry.y
bcen1 = bcen.drop('geometry', axis=1)

gclss['lon'] = gclss.geometry.x
gclss['lat'] = gclss.geometry.y
gclss1 = gclss.drop('geometry', axis=1)


st.header('Weekday Schedule Picker')
st.write('Choose a day -> the class that day will be displayed in order of time AND be shown on the map below it')

Week = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
#day = 0
day = st.selectbox("Weekday:", Week, index=0)
gc2['lon'] = gclss1['lon']
gc2['lat'] = gclss1['lat']
gc3 = gc2[gc2["Days"].str.contains(day)].sort_values(by=['Start'])
#st.write(day)
gc4 = gc3

distances = []
for i in range(0,len(gc4)-1):    
    g2 = gc4.iloc[[i]][['geometry', 'lon', 'lat']]
    ln = g2.iloc[0]['lon']
    lt = g2.iloc[0]['lat']
    g3 = g2[['geometry']]

    aeqd = CRS(proj='aeqd', ellps='WGS84', datum='WGS84', lat_0=lt, lon_0=ln).srs

    # Reproject to aeqd projection using Proj4-string
    g3 = g3.to_crs(crs=aeqd)

    g4 = g4.iloc[[i+1]][['geometry']].to_crs(crs=aeqd)

    g3_geom = g3['geometry'].iloc[0]

    g5 = calculate_distance(g4, dest_geom=g3_geom)

    #print(type(g5))
    #print(g5)
    distances.append(g5.iloc[0])
distances.append('None')

g4['Dist to Next Class'] = distances

st.dataframe(gc4)

#st.divider()

bcen1 = pd.DataFrame(bcen1)

map = folium.Map(location=[49.266048, -123.250012], zoom_start=15)
folium.GeoJson('geo_files/ubcv_buildings.geojson').add_to(map)


#for i in range(0,len(bcen1)):
#   folium.CircleMarker(
#      location=[bcen1.iloc[i]['lat'], bcen1.iloc[i]['lon']],
#      tooltip=bcen1.iloc[i]['NAME'], radius=3.5, fill=True, color='black', fillcolor='red', fillopacity=1
#   ).add_to(map)

for i in range(0,len(gc3)):
   tooltip = gc3.iloc[i]['Section']+'<br>'+gc3.iloc[i]['Start']+'<br>'+gc3.iloc[i]['NAME']+'<br>'+gc3.iloc[i]['Building']
   folium.Marker(
      location=[gc3.iloc[i]['lat'], gc3.iloc[i]['lon']],
      tooltip=folium.Tooltip(tooltip, style='width:300px; height:110px; white-space:normal;'), icon=folium.Icon(color='black')
   ).add_to(map)

st_map = st_folium(map, width=700, height=450)
st.write('Hover over the markers to see some more details')

#st.divider()

#st.map(bcen1, color="#ffaa0088", size=10.0)

#st.divider()
