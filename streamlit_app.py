import streamlit as st
import geopandas as gpd
import pandas as pd
# import numpy as np
import folium
from folium.features import DivIcon
from streamlit_folium import st_folium
from pyproj import CRS
from mapbox import Directions
# import os
from st_aggrid import AgGrid, GridOptionsBuilder
from gclss_prep import get_gclss

st.set_page_config(page_title='UBCV Class Map', page_icon=':bar_chart:', layout='wide')

st.title('UBC Vancouver - Class Map')
st.write("Map of the UBC Vancouver campus showing the location of your classes on any day!")
st.divider()
st.header('All My UBC Courses')

col1, col2, col3 = st.columns([0.45,0.1,0.45], vertical_alignment="center")

st.markdown(
    """
    <style>
        div[data-testid="column"]:nth-of-type(2)
        {
            text-align: center;
        }
        div[data-testid="column"]:nth-of-type(3)
        {
            text-align: center;
        }  
    </style>
    
    """,unsafe_allow_html=True
)


with col1: 
    uploaded_file = st.file_uploader("""**Upload your UBC Course List Excel file** (UNEDITED from Workday please) :) """,
                                    type="xlsx",
                                    help="""**Workday > Academics > Registration & Courses > View My Courses > "Export to Excel" icon on the top right corner above Enrolled Sections and click Download!**"""
                                )
    st.caption("Files uploaded are NEVER stored in anyway")
    if uploaded_file is not None:
        sample = False

with col2:
    st.write("OR")

with col3:
    sample = st.checkbox("Use sample data")


if uploaded_file is not None or sample is True:
    try:
        if sample:
            gclss_initial, name, terms = get_gclss("geo_files/ubc_View_My_Courses_unedited.xlsx")
            name = "Sample Schedule"
        else:    
            gclss_initial, name, terms = get_gclss(uploaded_file)

        st.subheader(name)
        term = st.selectbox("Choose Term:", terms, index=0)
        # st.write("selected term: "+term)

        gclss = gclss_initial[gclss_initial['Term']==term]
        gc = pd.DataFrame(gclss)
        gc1 = gclss.drop('geometry', axis=1)
        cols = ["Section", "Instructional Format", "Days", "Start", "End", "Room", "Building", "NAME", "Term"]
    
        gc1 = gc1[cols]
        st.dataframe(gc1)

        ########################
        ####
        # testing streamlit AgGrid library (paste code back here to play around again)

        #@#############33

        #st.sidebar.subheader("St-AgGrid example options")

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
        st.write('Hover over markers and green lines, or click on building outline to see more details ')
        st.write('Click the checkbox in the table to see wayfinding to the next class')
        Week = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
        #day = 0
        day = st.selectbox("Weekday:", Week, index=0)
        gc2['lon'] = gclss1['lon']
        gc2['lat'] = gclss1['lat']
        gc2['End'] = gc2['End'].astype('str')
        gc2['Start'] = gc2['Start'].astype('str')        
        # st.write(gc2['Start'][gc2['Start'].str.len() == 4])
        gc2['Start'][gc2['Start'].str.len() == 4] = "0" + gc2['Start']
        gc2['End'][gc2['End'].str.len() == 4] = "0" + gc2['End']
        # st.write(gc2['Start'])

        # print(f"string lenghts of Start = {gc2['Start'].str.len()}")
        gc3 = gc2[gc2["Days"].str.contains(day)].sort_values(by=['Start'])
        # gc3 is still geopandas Dataframe
        # gc4 is already normal pandas Dataframe

        gc4 = pd.DataFrame(gc3)
        gc4 = gc4.drop('geometry', axis=1)
        l = []
        for i in range(1, len(gc4)+1):
            #print(i)
            l.append(i)
        gc4['Order'] = l
        gc4['order2'] = l
        gc4 = gc4.set_index('Order')

        #st.write(day)

        def title(row):
            name = row["Section"]+" ("+row["Building"]+")"
            return name

        l1 = []
        for i in range (0, len(gc4)-1):
            l1.append(i)
            #st.write(i)

        service = Directions(access_token=st.secrets['MAPBOX_ACCESS_TOKEN'])

        #st.write("response code: ", str(response.status_code))

        #ind = st.selectbox("Wayfinding:", l1, format_func=lambda x: title(gc3.iloc[x])+" -- to -- "+title(gc3.iloc[x+1]), placeholder="None", index=None)
        #st.write("selected index: ", ind)

        # distances = []
        dist_list = []
        time_list = []
        directions = []
        for i in range(0,len(gc3)-1):    
            # g2 = gc3.iloc[[i]][['geometry', 'lon', 'lat']]
            # ln = g2.iloc[0]['lon']
            # lt = g2.iloc[0]['lat']
            # g3 = g2[['geometry']]

            # aeqd = CRS(proj='aeqd', ellps='WGS84', datum='WGS84', lat_0=lt, lon_0=ln).srs

            # # Reproject to aeqd projection using Proj4-string
            # g3 = g3.to_crs(crs=aeqd)

            # g4 = gc3.iloc[[i+1]][['geometry']].to_crs(crs=aeqd)

            # g3_geom = g3['geometry'].iloc[0]

            # g5 = calculate_distance(g4, dest_geom=g3_geom)

            # #print(type(g5))
            # #print(g5)
            # distances.append(g5.iloc[0])

        ## MAPBOX direction api
            origin = {
            'type': 'Feature',
            'properties': {'name': gc3.iloc[i]['Building']},
            'geometry': {
                'type': 'Point',
                'coordinates': [gc3.iloc[i]['lon'].item(), gc3.iloc[i]['lat'].item()]}}
            destination = {
            'type': 'Feature',
            'properties': {'name': gc3.iloc[i+1]['Building']},
            'geometry': {
                'type': 'Point',
                'coordinates': [gc3.iloc[i+1]['lon'].item(), gc3.iloc[i+1]['lat'].item()]}}

            response = service.directions([origin, destination],'mapbox/walking')
            print("response code: ", response.status_code)

            walking_route = response.geojson()
            wdist = walking_route['features'][0]['properties']['distance']
            wdist = wdist/1000
            wdstr = float(str("%.3f" % wdist))

            wtime = walking_route['features'][0]['properties']['duration']
            wtime = wtime/60
            wtstr = float(str("%.2f" % wtime))

            dist_list.append(wdstr)
            time_list.append(wtstr)
            directions.append(walking_route)

        # distances.append(None)
        dist_list.append(None)
        time_list.append(None)
        #st.write("dist_list: ", dist_list)
        #st.write("distances: ", distances)
        # gc4['Dist to Next Class /km'] = distances
        gc4['Walking distance /km'] = dist_list
        gc4['Walking duration /min'] = time_list

        #st.write("directions: ", directions)

        gc4_cols = ["Section", "Instructional Format", "Start", "End", "Building", "Room", "Walking distance /km", "Walking duration /min"]
        #st.dataframe(gc4[gc4_cols])

        colm, colt = st.columns([0.4, 0.6])

        ####################
        ###### AGGRID ######
        gc5 = gc4
        gc5["Order"] = l
        gcc = gc5["Section"].str.split(" - ", expand=True)
        gc5["Section"] = gcc[0]
        gc5_cols = ["Order", "Section", "Instructional Format", "Start", "End", "Building", "Room", "Walking distance /km", "Walking duration /min", "lon", "lat"]
        gc5 = gc5[gc5_cols]
        gb = GridOptionsBuilder.from_dataframe(gc5)
        #make all columns editable
        #gb.configure_columns(cols, editable=True)
        selection_mode='single'
        gb.configure_selection(selection_mode)

        if len(gc5)==1:
            checkbox = False
        else:
            checkbox = True

        gb.configure_selection(
                    selection_mode,
                    use_checkbox=checkbox)
        gb.configure_columns(["lon", "lat"], hide=True)

        gb.configure_column(field="Section", header_name="Course")
        gb.configure_column(field="Instructional Format", header_name="Format")
        gb.configure_column(field="Building", header_name="Bldg")
        gb.configure_column(field="Walking distance /km", header_name="Walking Distance (km)")
        gb.configure_column(field="Walking duration /min", header_name="Walking Duration (min)")

        with colt:
            # expand = st.toggle("expand all columns", 
            #                    help="click if can't read content of the table",
            #                    value=False,
            #                    label_visibility="hidden",
            #                    disabled=True
            #                    )
            
            
            gb.configure_default_column(
                wrapText=True, 
                wrapHeaderText=True, 
                autoHeight=True, 
                autoHeaderHeight=True, 
                filterable=False,
                suppressMovable=True, 
                # suppressSizeToFit=False,
                minWidth=20,
                # maxWidth=80
            )
            gb.configure_grid_options(autoSizeStrategy={type: 'fitCellContents'})
           
            go = gb.build()
            # if expand:
            #     grid_response = AgGrid(
            #         gc5, 
            #         gridOptions=go
            #     )
            # else:
            #     grid_response = AgGrid(
            #         gc5, 
            #         gridOptions=go,  
            #         fit_columns_on_grid_load=True
            #     )

            grid_response = AgGrid(
                    gc5, 
                    gridOptions=go,  
                    fit_columns_on_grid_load=True
                )

        #selected = pd.DataFrame()
        selected = grid_response["selected_rows"]
        #st.write("selected row: ", selected)
        #try:
        #    st.write("section: ", selected[["Section"]])
        #except TypeError:
        #    st.write("selected is None")

        ####### AGGRID END
        #######

        #gclss[["Section", "Instructional Format", "Days", "Start", "End", "Room", "Building"]]
        # st.write('Hover over the markers to see some more details')

        #st.divider()

        bcen1 = pd.DataFrame(bcen1)

        geoj = 'geo_files/ubcv_buildings.geojson'
        bldg = gpd.read_file(geoj)
        bldg2 = bldg.to_crs(epsg=3857)
        #st.write(bldg2.crs)

        lon_med = gc3['lat'].mean()
        lat_med = gc3['lon'].mean()
        # st.text(str(lon_med)+", "+str(lat_med))
        # location=[49.266048, -123.250012]

        map = folium.Map(location=[lon_med, lat_med], zoom_start=15, min_zoom=14, control_scale=True)
        fields = ["NAME", "BLDG_CODE", "BLDG_USAGE"]
        alias = ["Name", "Code", "Usage"]
        popup = folium.features.GeoJsonPopup(fields, alias)
        folium.GeoJson(bldg2, popup=popup).add_to(map)

        #for i in range(0,len(bcen1)):
        #   folium.CircleMarker(
        #      location=[bcen1.iloc[i]['lat'], bcen1.iloc[i]['lon']],
        #      tooltip=bcen1.iloc[i]['NAME'], radius=3.5, fill=True, color='black', fillcolor='red', fillopacity=1
        #   ).add_to(map)

        #gc3[['lon', 'lat']]
        #oval = gc3.iloc[0]['lon'].item()
        #pyval  = oval.item()
        #print(type(oval))
        #gc3.iloc[1]['Building']

        for i in range(0,len(gc3)):
            rw = gc3.iloc[i]
            loc = [rw['lat'], rw['lon']]
            tooltip = rw['Section']+'<br>'+rw['Start']+'<br>'+rw['NAME']+'<br>'+rw['Building']+'<br>'+rw['Room']

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
                        html="""<span class="fa-stack " style="font-size: 12pt; color: white" >
                                <!-- The icon that will wrap the number -->
                                <span class="fa fa-circle-o fa-stack-2x"></span>
                                <!-- a strong element with the custom content, in this case a number -->
                                <strong class="fa-stack-1x">
                                    {:02d}  
                                </strong>
                            </span>""".format(i+1)
                    )
                ).add_to(map)

        # try: 
            #
        if selected is not None:
            ind = int(selected["Order"].iloc[0])-1
            
            if ind+1 == len(gc3):
                ind = ind-1

            w = directions[ind]['features'][0]['geometry']['coordinates']

            coord2 = []
            for i in range(0, len(w)):
                list = [w[i][1], w[i][0]]
                coord2.append(list)
            #st.write("COORDINATES")
            #st.table(coord2)

            tt = str(ind+1)+'. '+gc3.iloc[ind]["NAME"]+' <b>('+gc3.iloc[ind]['Building']+') -</b> <br>'+str(ind+2)+'. '+gc3.iloc[ind+1]["NAME"]+' <b>('+gc3.iloc[ind+1]['Building']+')</b>'

            folium.PolyLine(
            locations=coord2,
            color="#06402B",
            weight=6,
            tooltip=folium.Tooltip(tt, style='width:300px; height:80px;white-space:normal;'),
                ).add_to(map)

            #list_ind = [ind, ind+1]
            for i in [ind, ind+1]:
                row = gc3.iloc[i]
                loc = [row['lat'], row['lon']]
                tooltip = row['Section']+'<br>'+row['Start']+'<br>'+row['NAME']+'<br>'+row['Building']+'<br>'+row['Room']

                folium.Marker(
                    location=loc,
                    #popup="Delivery " + '{:02d}'.format(i+1),
                    tooltip=folium.Tooltip(tooltip, style='width:300px; height:110px; white-space:normal;'), 
                    icon=folium.Icon(color='red',icon_color='red'),
                ).add_to(map)

                folium.Marker(
                        location=loc,
                        #popup="Delivery " + '{:02d}'.format(i+1),
                        tooltip=folium.Tooltip(tooltip, style='width:300px; height:110px; white-space:normal;'), 
                        icon= DivIcon(
                            icon_size=(30,30),
                            icon_anchor=(18,40),
                #             html='<div style="font-size: 18pt; align:center, color : black">' + '{:02d}'.format(num+1) + '</div>',
                            html="""<span class="fa-stack " style="font-size: 12pt; color: white" >
                                    <!-- The icon that will wrap the number -->
                                    <span class="fa fa-circle-o fa-stack-2x" ></span>
                                    <!-- a strong element with the custom content, in this case a number -->
                                    <strong class="fa-stack-1x">
                                        {:02d}  
                                    </strong>
                                </span>""".format(i+1)
                        )
                    ).add_to(map)
        # except AttributeError:
            #st_map = st_folium(map, width=700, height=450)
            # st.write(selected)

        with colm:
            st_map = st_folium(map, height=480, width='100%')


    except ValueError:
        st.error("Sorry... your file is incompatible with our system", icon="🔥")



## adding a footer
footer_html = """ 
<style> 
    .footer {
        position: relative;
        left: 0;
        bottom: -100px;
        width: 100%;
        background-color: white;
        color: black;
        text-align: center;
        font-size: 10px;
        padding-top: 20px;
        padding-bottom: 20px
    }
</style>

<div class="footer">
  <p>Personal project developed by Athalia R Setiawan (UBC '28) (athalia22rs@gmail.com) -- August 2024 :D</p>
  <p>Map data downloaded from <a href="https://github.com/UBCGeodata/ubc-geospatial-opendata">UBC geospatial data Github</a> in July 2024</p>
  <p>Disclaimers: No guarantee on the accuracy of the information displayed on this site.
    This site is not affiliated with UBC </p>
    
</div>"""
st.markdown(footer_html, unsafe_allow_html=True)