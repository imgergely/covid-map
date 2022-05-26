# %%
import folium
from folium.plugins import TimestampedGeoJson
import geopandas as gpd
import pandas as pd
import branca
import branca.colormap

# %%
geodf = gpd.read_file("HUN_adm1.shp")
geodf.set_index('NAME_1', inplace=True)

# %%
covidf = pd.read_csv("data-WLVSF.csv")
covidf["X.1"] = pd.to_datetime(covidf["X.1"])
covidf["X.1"] = covidf["X.1"].dt.strftime('%Y-%m-%d')
covidftrans = covidf.T
covidftrans.columns = covidftrans.iloc[0]
covidftrans = covidftrans[1:-2]

# %%
colmin = []
colmax = []
for column in covidftrans:
    colmin.append(covidftrans[column].min())
    colmax.append(covidftrans[column].max())
dfmin = min(colmin)
dfmax = max(colmax)

# %%
merged = pd.DataFrame
merged = pd.merge(geodf,covidftrans,left_index=True, right_index=True)

# %%
m = folium.Map(location=[47.1718531,19.5013194],
           zoom_start=7.5, min_zoom=7, max_zoom=8,
           tiles='https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}', attr = 'Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ')

color = branca.colormap.linear.YlOrRd_09.scale(dfmin,dfmax)
color.caption = 'Újonnan azonosított fertőzött / 100.000 lakos'
color.add_to(m)

style = lambda x: {'fillColor': '#d3d3d3','color': 'black'}
for i in range(len(merged.index)):
    folium.GeoJson(merged.iloc[[i]], name="Geo", style_function=style).add_to(m)


# %%
geo = {}
for  index,row in merged.iterrows():
    geo[index] = [row.geometry.centroid.x,row.geometry.centroid.y]

features = []
for column in merged.columns[9:]:
    for index, value in merged[column].items():
        feature = {'type': 'Feature',
        'geometry': {
            'type':'Point', 
            'coordinates': geo.get(index)
        },
        'properties': {
            'times': [column]*2,
            'popup': "Azonosított fertőzött : " + str(round(value)), 
            'icon': 'circle',
            'style': {'color' : ''},
            'iconstyle':{
                'fillColor': color.rgb_hex_str(value),
                'fillOpacity': 0.8,
                'radius': value / 3
                }
            }
        }
        features.append(feature)

# %%


TimestampedGeoJson({ 'type': 'FeatureCollection', 'features': features},period="P1D", duration="P1D",transition_time=100,  min_speed=15, max_speed=30).add_to(m)

m.save("map.html")

m


