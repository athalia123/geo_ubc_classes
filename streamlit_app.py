import streamlit as st
import geopandas as gpd
import pandas as pd

st.title('My First App - Hello World :)')
st.write("I'm going to make a map of the campus and put my classes on it")

gclss = gpd.read_file("geo_files/geoclass1.geojson")
gc = pd.DataFrame(gclss)

st.table(gc)

