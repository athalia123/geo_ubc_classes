import geopandas as gpd
import pandas as pd


def get_time(period, mpa):
    mp2 = mpa[2].str.split(" \- ", expand=True)
    mp2.columns = ['Start', 'End']

    time = mp2[period]
    st2 = time.str.split(expand=True)
    st3 = st2[st2[1].str.contains("p")]
    st4 = st3[0].str.split(":", expand=True)

    for i in st4.index:
        if int(st4[0].loc[i]) < 12:
            st4.loc[i, 0] = str(int(st4[0].loc[i])+12)
    st4[2] = st4[0]+":"+st4[1]

    st6 = st2
    for i in st4.index:
        st6.loc[i, 0] = st4[2].loc[i]
    #st6[[0]]
    #mp5['End1'] = st6[0]
    return st6[0]

def get_gclss(file_name):
    #x = pd.read_excel("geo_files/ubc_View_My_Courses_unedited.xlsx", engine='openpyxl')

    try:
        x = pd.read_excel(file_name, engine='openpyxl')
        df = pd.DataFrame(x)
        df.drop(0, axis='index', inplace=True)
        colname = list(df.columns)

        str1 = df.loc[2, 'My Enrolled Courses'].split(" - ")
        name = str1[0]

        enc = df[colname[0]]
        enc.drop(1, axis='index', inplace=True)
        dft = enc.str.rsplit(" (", expand=True, n=1)
        term = dft[0].str.rsplit(" - ", expand=True, n=1)[1]

        df.drop(colname[0], axis='columns', inplace=True)

        # rename the columns
        df.columns = list(df.iloc[0])
        df.drop(1, axis='index', inplace=True)

         # drop columns "Drop" and "Swap" if they exist
        df_col = df.columns
        if "Drop" in df_col:
            df.drop('Drop', axis='columns', inplace=True)
        if "Swap" in df_col:
            df.drop('Swap', axis='columns', inplace=True)

        # delete row with empty meeting patterns
        msv = df[pd.isna(df['Meeting Patterns'])].index
        df.drop(msv, axis='index', inplace=True)

        # keep only classes that are registered
        nnr = df[df['Registration Status']!="Registered"].index
        df.drop(nnr, axis='index', inplace=True)
        #print(nnr)

        # Get buidling code, floor, room
        mpa = df['Meeting Patterns'].str.split(" \| ", expand=True)
        bfr_ind = mpa.columns
        bfr = mpa[bfr_ind[-1]].str.split("-", n=1,expand=True)
        df[['Building', 'Room']] = bfr

        # Get days
        df["Days"] = mpa[1]

        # Get start and end time
        df["Start"] = get_time("Start", mpa)
        df["End"] = get_time("End", mpa)

        df["Term"] = term 

        # drop meeting patterns column
        df.drop("Meeting Patterns", axis='columns', inplace=True)

        df.reset_index(drop=True, inplace=True)

        # reorder the columns
        df2 = df.iloc[:, [3,1,2,4,5,6,12,13,14,10,11,7,8,9,15]]


        course = gpd.GeoDataFrame(df2)
        bcen = gpd.read_file("geo_files/ubc_buildings_centroids.geojson")

        bcen1 = bcen[['BLDG_CODE', 'NAME', 'SHORTNAME', 'POSTAL_CODE', 'PRIMARY_ADDRESS', 'geometry']]

        gclss = course.merge(bcen1, left_on='Building', right_on='BLDG_CODE')
        gclss.drop("BLDG_CODE", axis='columns', inplace=True)
        gclss1 = gpd.GeoDataFrame(gclss)

        print("ALL COLUMNS: ", df.columns)
        terms = df2['Term'].unique()

        return gclss1, name, terms
    except IndexError or ValueError or AttributeError or KeyError:
        return "Sorry... something went wrong during the file processing"

