import pandas as pd
import numpy as np
import json
from datetime import datetime
import matplotlib.pyplot as plt

with open('History.json') as f:
    d = json.load(f)

data = pd.json_normalize(d['locations'])
print(data.head(3))

def timefmt(x):
    return datetime.fromtimestamp(int(x))

output = pd.DataFrame()
output['timestampMs'] = data['timestampMs'].astype('float') / 1000
output['timestamp'] = output['timestampMs'].apply(timefmt)
output['latitudeE7'] = data['latitudeE7'].astype('float') / 10000000
output['longitudeE7'] = data['longitudeE7'].astype('float') / 10000000
output['altitude'] = data['altitude'].astype('double')

#Sort the output DataFrame
output = output.sort_values(by=['timestamp'], axis=0)
output = output.drop_duplicates(subset=['timestamp'], keep='first')
print(output.head(3))

from math import radians, cos, sin, asin, sqrt

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r

#Calculate Time Delta
output['tdelta'] = (output.timestamp - output.timestamp.shift()).\
    fillna(pd.Timedelta(seconds=0))
output['tdelta'] = output['tdelta'] / np.timedelta64(1, 'm')


#Point of Interest
ilat = 61.1234
ilong = -149.45678

#Radius - includes all points within this distance from point of interest
radius = 250 #Meters
radius = radius / 1000 #Kilometers


#Calculate the distance
output['distance'] = output.apply(lambda x: haversine(ilong, ilat, \
    x.longitudeE7, x.latitudeE7), axis=1)


#filter by distance and group by date
output['date'] = output['timestamp'].dt.floor('d')
output['tdelta'] = output['tdelta'] / 60  #minutes to hours
output = output[output['distance'] < radius]
output = output[['date', 'tdelta']]
output = output.groupby(output['date']).sum()
print(output.head(100))



fig, ax = plt.subplots()
ax.bar(output.index, output.tdelta)
ax.axes.set_xlabel("Date")
ax.axes.set_ylabel("Hours Worked (tdelta)")