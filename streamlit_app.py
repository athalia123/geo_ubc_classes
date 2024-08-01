import streamlit as st
import geopandas as gpd
import pandas as pd

st.title('My First App - Hello World :)')
st.write("I'm going to make a map of the campus and put my classes on it")


gclss = gpd.read_file("geo_files/geoclass1.geojson")
gc = pd.DataFrame(gclss)
gc1 = gc.drop('geometry', axis=1)
gc2 = gc1[["Section", "Instructional Format", "Days", "Start", "End", "Room", "Building", "SHORTNAME"]]
st.dataframe(gc2)
