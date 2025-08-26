import geopandas as gpd
import pandas as pd


def get_time(period, mpa):
    mp2 = mpa.str.split(" \- ", expand=True)
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

        nameDetails = df["My Enrolled Courses"]
        nameDetails.drop(1, axis="index", inplace=True)
        df.drop("My Enrolled Courses", axis='columns', inplace=True)

        details_split = nameDetails.str.rsplit(" - ", expand=True, n=1)
        name_id_split = details_split[0].str.split(" - ", expand=True, n=1)[0]
        terms = details_split[1].str.rsplit(" (", expand=True, n=1)[0]
        name = name_id_split.iloc[0]

        # str1 = df.loc[2, 'My Enrolled Courses'].split(" - ")
        # name = str1[0]

        # enc = df[colname[0]]
        # enc.drop(1, axis='index', inplace=True)
        # dft = enc.str.rsplit(" (", expand=True, n=1)
        # term = dft[0].str.rsplit(" - ", expand=True, n=1)[1]

        # df.drop(colname[0], axis='columns', inplace=True)

        

        # rename the columns
        df.columns = list(df.iloc[0])
        df.drop(1, axis='index', inplace=True)

        df["Term"] = terms

         # drop columns "Drop" and "Swap" if they exist
        df_col = df.columns
        if "Drop" in df_col:
            df.drop('Drop', axis='columns', inplace=True)
        if "Swap" in df_col:
            df.drop('Swap', axis='columns', inplace=True)
        df.drop(["Credits", "Grading Basis"], axis="columns", inplace=True)

        # delete row with empty meeting patterns
        msv = df[pd.isna(df['Meeting Patterns'])].index
        df.drop(msv, axis='index', inplace=True)

        # keep only classes that are registered
        nnr = df[df['Registration Status']!="Registered"].index
        df.drop(nnr, axis='index', inplace=True)
        #print(nnr)

        # get meeting patters
        mpa_raw = df["Meeting Patterns"]
        mpa_split = mpa_raw.str.split("\n\n", expand=True)
        mpa_nodate = mpa_split[0].str.split("|", expand=True, n=1)[1]
        mpa_nodate1 = mpa_split[1].str.split("|", expand=True, n=1)[1]

        df.drop(["Meeting Patterns"], axis="columns", inplace=True)
        df["mpa0"] = mpa_nodate
        df["mpa1"] = mpa_nodate1
        df.reset_index(inplace=True)
        mpa_multiple_df = df[(df["mpa0"] != df["mpa1"]) & (df["mpa1"].notna())]


        for row in mpa_multiple_df.index:
            ind = len(df)
            df.loc[ind] = df.loc[row].copy()
            df.loc[ind, "mpa0"] = df.loc[row, "mpa1"]

        df.drop("mpa1", axis="columns", inplace=True)

        # Get buidling code, floor, room
        mpa_parse = df['mpa0'].str.split(" \| ", expand=True)
        buildings = mpa_parse[3].str.split(" \(", expand=True)[1].str.split("\)", expand=True)[0]

        df["Building"] = buildings

        # Get days
        df["Days"] = mpa_parse[0]

        floor = mpa_parse[4].str.split(":", expand=True)
        room = mpa_parse[5].str.split(":", expand=True)
        mpa_parse["Room"] = floor[0] + floor[1] + "-" + room[0] + room[1]

        df["Room"] = mpa_parse["Room"]

        # Get start and end time
        time = mpa_parse[1]
        df["Start"] = get_time("Start", time)
        df["End"] = get_time("End", time)

       

        # drop meeting patterns column
        df.drop("mpa0", axis='columns', inplace=True)

        df.reset_index(drop=True, inplace=True)

        # reorder the columns
        # df2 = df.iloc[:, [3,1,2,4,5,6,12,13,14,10,11,7,8,9,15]]


        course = gpd.GeoDataFrame(df)
        bcen = gpd.read_file("geo_files/ubc_buildings_centroids.geojson")

        bcen1 = bcen[['BLDG_CODE', 'NAME', 'SHORTNAME', 'POSTAL_CODE', 'PRIMARY_ADDRESS', 'geometry']]

        gclss = course.merge(bcen1, left_on='Building', right_on='BLDG_CODE')
        gclss.drop("BLDG_CODE", axis='columns', inplace=True)
        gclss1 = gpd.GeoDataFrame(gclss)
        print("gclss1: ", gclss1)

        print("ALL COLUMNS: ", df.columns)
        terms = df["Term"].unique()
        terms = terms[terms.notna()]

        return gclss1, name, terms

    except IndexError or ValueError or AttributeError or KeyError:
        return "Sorry... something went wrong during the file processing"

