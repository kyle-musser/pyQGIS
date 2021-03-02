from geopy.distance import lonlat, geodesic
import pandas as pd
import os

# Set current directory of files
os.chdir(r"D:/cenBlock")

# Read in NCES directory 2018 CSV to Pandas DF (this data made in stata with .do file ("get_nces_dir.do")
cenBlks = pd.read_csv("points_AlbersXY.csv")

# Get list of unique states to loop through
states = cenBlks.state_abbrev.unique()

# loop through states to make distance matrix for each state one at a time.
for state in states:
    print("Calculating Distance Matrix for State: ", state)

    st_dat = cenBlks[cenBlks['state_abbrev'] == str(state)]  # subset to one state (current state in the loop)
    st_dat = st_dat[['GEOID10', 'lat', 'lon']]  # only keep lat/lon and ID variables

    # using merge to generate all possibilities between origin and destination
    # this will make an (N^2 x 6) length matrix with all possible combinations of lat/lon in the state
    df = pd.merge(st_dat.assign(key=0), st_dat.assign(key=0), suffixes=('', '_x'), on='key').drop('key', axis=1)

    # Use geopy to calculate miles between all nces combinations in the dataframe we just made
    df['Miles'] = df.apply(
       (lambda row: geodesic(lonlat(row['lon'], row['lat']),
                             lonlat(row['lon_x'], row['lat_x'])).miles), axis=1)

    # Now reshape the data to look like the distance matrix we want
    df = df.groupby(['GEOID10', 'GEOID10_x'])['Miles'].max().unstack()

    # Add in state variable to dataset as first variable
    df.insert(0, 'state', [state] * len(df))

    # Save each unique state distance matrix
    flnm = "stateDistances/" + state + "distMatrix.csv"
    df.to_csv(flnm)
