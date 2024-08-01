import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
from streamlit_folium import st_folium

st.title('My First App - Hello World :)')
st.write("I'm going to make a map of the campus and put my classes on it")


gclss = gpd.read_file("geo_files/geoclass1.geojson")
gc = pd.DataFrame(gclss)
gc1 = gc.drop('geometry', axis=1)
gc2 = gc1[["Section", "Instructional Format", "Days", "Start", "End", "Room", "Building", "SHORTNAME"]]
st.dataframe(gc2)

st.divider()

bcen = gpd.read_file("geo_files/ubc_buildings_centroids.geojson")
bcen['lon'] = bcen.geometry.x
bcen['lat'] = bcen.geometry.y
bcen1 = bcen.drop('geometry', axis=1)
st.map(bcen1, color="#ffaa0088", size=10.0)

st.divider()

Week = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
day = 0
gc3 = gc2[gc2["Days"].str.contains(Week[day])]
st.header(Week[day])
st.dataframe(gc3)

st.divider()

bcen1 = pd.DataFrame(bcen1)

map = folium.Map(location=[49.266048, -123.250012], zoom_start=15)
folium.GeoJson('geo_files/ubcv_buildings.geojson').add_to(map)

for i in range(0,len(bcen1)):
   folium.CircleMarker(
      location=[bcen1.iloc[i]['lat'], bcen1.iloc[i]['lon']],
      tooltip=bcen1.iloc[i]['NAME'], radius=3.5, fill=True, color='black', fillcolor='red', fillopacity=1
   ).add_to(map)

st_map = st_folium(map, width=700, height=450)

