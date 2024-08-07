import streamlit as st
import geopandas as gpd
import pandas as pd
import numpy as np
import folium
from folium.features import DivIcon
from streamlit_folium import st_folium
from pyproj import CRS
from mapbox import Directions
import os

st.set_page_config(page_title='UBCV Class Map', page_icon=':bar_chart:', layout='wide')

st.title('My First App - Hello World :)')
st.write("I'm going to make a map of the campus and put my classes on it")

st.divider()

st.header('All My UBC Courses')
gclss = gpd.read_file("geo_files/geoclass1.geojson")
gc = pd.DataFrame(gclss)
gc1 = gc.drop('geometry', axis=1)
gc1 = gc1[["Section", "Instructional Format", "Days", "Start", "End", "Room", "Building", "NAME"]]
st.dataframe(gc1)

gc2 = gclss[["Section", "Instructional Format", "Days", "Start", "End", "Room", "Building", "NAME", "geometry"]]

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

gc4 = pd.DataFrame(gc3)
gc4 = gc4.drop('geometry', axis=1)
l = []
for i in range(1, len(gc4)+1):
    #print(i)
    l.append(i)
gc4['Order'] = l
gc4 = gc4.set_index('Order')

#st.write(day)

def title(row):
    name = row["Section"]+" ("+row["Building"]+")"
    return name

l1 = []
for i in range (0, len(gc4)-1):
    l1.append(i)
    #st.write(i)

ind = st.selectbox("Wayfinding:", l1, format_func=lambda x: title(gc3.iloc[x])+" to "+title(gc3.iloc[x+1]), placeholder="None", index=None)
st.write("selected index: ", ind)

distances = []
for i in range(0,len(gc3)-1):    
    g2 = gc3.iloc[[i]][['geometry', 'lon', 'lat']]
    ln = g2.iloc[0]['lon']
    lt = g2.iloc[0]['lat']
    g3 = g2[['geometry']]

    aeqd = CRS(proj='aeqd', ellps='WGS84', datum='WGS84', lat_0=lt, lon_0=ln).srs

    # Reproject to aeqd projection using Proj4-string
    g3 = g3.to_crs(crs=aeqd)

    g4 = gc3.iloc[[i+1]][['geometry']].to_crs(crs=aeqd)

    g3_geom = g3['geometry'].iloc[0]

    g5 = calculate_distance(g4, dest_geom=g3_geom)

    #print(type(g5))
    #print(g5)
    distances.append(g5.iloc[0])
distances.append(None)

gc4['Dist to Next Class /km'] = distances

st.dataframe(gc4[["Section", "Instructional Format", "Start", "End", "Building", "Room", "Dist to Next Class /km"]])
#gclss[["Section", "Instructional Format", "Days", "Start", "End", "Room", "Building"]]
st.write('Hover over the markers to see some more details')

#st.divider()

bcen1 = pd.DataFrame(bcen1)

geoj = 'geo_files/ubcv_buildings.geojson'
bldg = gpd.read_file(geoj)
bldg2 = bldg.to_crs(epsg=3857)
#st.write(bldg2.crs)

map = folium.Map(location=[49.266048, -123.250012], zoom_start=15, min_zoom=14, control_scale=True)
folium.GeoJson(bldg2).add_to(map)

#for i in range(0,len(bcen1)):
#   folium.CircleMarker(
#      location=[bcen1.iloc[i]['lat'], bcen1.iloc[i]['lon']],
#      tooltip=bcen1.iloc[i]['NAME'], radius=3.5, fill=True, color='black', fillcolor='red', fillopacity=1
#   ).add_to(map)

for i in range(0,len(gc3)):
   loc = [gc3.iloc[i]['lat'], gc3.iloc[i]['lon']]
   tooltip = gc3.iloc[i]['Section']+'<br>'+gc3.iloc[i]['Start']+'<br>'+gc3.iloc[i]['NAME']+'<br>'+gc3.iloc[i]['Building']

   folium.Marker(
      location=loc,
      #popup="Delivery " + '{:02d}'.format(i+1),
      tooltip=folium.Tooltip(tooltip, style='width:300px; height:110px; white-space:normal;'), 
      icon=folium.Icon(color='black',icon_color='black'),
        markerColor='pink',
   ).add_to(map)

   folium.Marker(
        location=loc,
        #popup="Delivery " + '{:02d}'.format(i+1),
        tooltip=folium.Tooltip(tooltip, style='width:300px; height:110px; white-space:normal;'), 
        icon= DivIcon(
            icon_size=(30,30),
            icon_anchor=(18,40),
#             html='<div style="font-size: 18pt; align:center, color : black">' + '{:02d}'.format(num+1) + '</div>',
            html="""<span class="fa-stack " style="font-size: 12pt" >
                    <!-- The icon that will wrap the number -->
                    <span class="fa fa-circle-o fa-stack-2x" style="color : black"></span>
                    <!-- a strong element with the custom content, in this case a number -->
                    <strong class="fa-stack-1x">
                         {:02d}  
                    </strong>
                </span>""".format(i+1)
        )
    ).add_to(map)
   
#gc3[['lon', 'lat']]
#oval = gc3.iloc[0]['lon'].item()
#pyval  = oval.item()
#print(type(oval))
#gc3.iloc[1]['Building']

if ind!=None:
    service = Directions(access_token="pk.eyJ1IjoiYXRoYWxpYS0xNzIzIiwiYSI6ImNsemZvNTEwcTEyZWIyc3EwOWtydHdlMGIifQ.QI-Y0g3fxAOGJfl_9vE6MQ")
    #service = Directions(access_token=os.environ['MAPBOX_ACCESS_TOKEN'])
    #service.session.params['access_token']
    origin = {
        'type': 'Feature',
        'properties': {'name': gc3.iloc[ind]['Building']},
        'geometry': {
            'type': 'Point',
            'coordinates': [gc3.iloc[ind]['lon'].item(), gc3.iloc[ind]['lat'].item()]}}
    destination = {
        'type': 'Feature',
        'properties': {'name': gc3.iloc[ind+1]['Building']},
        'geometry': {
            'type': 'Point',
            'coordinates': [gc3.iloc[ind+1]['lon'].item(), gc3.iloc[ind+1]['lat'].item()]}}

    response = service.directions([origin, destination],
        'mapbox/walking')
    print("response code: ", response.status_code)

    #st.write("response code: ", str(response.status_code))

    walking_route = response.geojson()
    w = walking_route['features'][0]['geometry']['coordinates']

    coord2 = []
    for i in range(0, len(w)):
        list = [w[i][1], w[i][0]]
        coord2.append(list)
    #st.write("COORDINATES")
    #st.table(coord2)

    tt = gc3.iloc[ind]["NAME"]+' ('+gc3.iloc[ind]['Building']+') - <br>'+gc3.iloc[ind+1]["NAME"]+' ('+gc3.iloc[ind+1]['Building']+')',

    folium.PolyLine(
    locations=coord2,
    color="#FF0000",
    weight=3,
    tooltip=folium.Tooltip(tt, style='width:300px; height:80px;white-space:normal;'),
        ).add_to(map)

    list_ind = [ind, ind+1]
    for i in list_ind:
        row = gc3.iloc[i]
        loc = [row['lat'], row['lon']]
        tooltip = row['Section']+'<br>'+row['Start']+'<br>'+row['NAME']+'<br>'+row['Building']

        folium.Marker(
            location=loc,
            #popup="Delivery " + '{:02d}'.format(i+1),
            tooltip=folium.Tooltip(tooltip, style='width:300px; height:110px; white-space:normal;'), 
            icon=folium.Icon(color='black',icon_color='black'),
        ).add_to(map)

        folium.Marker(
                location=loc,
                #popup="Delivery " + '{:02d}'.format(i+1),
                tooltip=folium.Tooltip(tooltip, style='width:300px; height:110px; white-space:normal;'), 
                icon= DivIcon(
                    icon_size=(30,30),
                    icon_anchor=(18,40),
        #             html='<div style="font-size: 18pt; align:center, color : black">' + '{:02d}'.format(num+1) + '</div>',
                    html="""<span class="fa-stack " style="font-size: 12pt" >
                            <!-- The icon that will wrap the number -->
                            <span class="fa fa-circle-o fa-stack-2x" style="color : white"></span>
                            <!-- a strong element with the custom content, in this case a number -->
                            <strong class="fa-stack-1x">
                                {:02d}  
                            </strong>
                        </span>""".format(i+1)
                )
            ).add_to(map)



   


#folium.Icon(color='black')

st_map = st_folium(map, width=700, height=450)

#st.divider()

#st.map(bcen1, color="#ffaa0088", size=10.0)

#st.divider()
