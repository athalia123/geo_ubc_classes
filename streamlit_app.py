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

bcen1 = pd.DataFrame(bcen1)
map = folium.Map(location=[49.262548, -123.245112], zoom_start=15)
folium.GeoJson('geo_files/ubcv_buildings.geojson').add_to(map)

for i in range(len(bcen1)):
    icon=folium.Icon(color="black")
    folium.geojson.add_child(folium.Marker((bcen[i, 'Latitude'],bcen[i, 'Longitude']), icon=icon))

st_map = st_folium(map, width=700, height=450)

