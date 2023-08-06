import pandas as pd
import requests
import sklearn.preprocessing

STATIONS_URL = "https://www.mvg.de/api/fahrinfo/location/queryWeb?q="
PROXIES = {
    "http": "http://10.182.0.21:80",
    "https": "http://10.182.0.21:80"
}


def get_stations():
    """
    Gets all stations in the MVV, including their coordinates and means of transport available there.
    """
    req = requests.get(STATIONS_URL, proxies=PROXIES)
    data = req.json()
    stations = pd.DataFrame(data["locations"])
    
    stations = stations[(stations.place == "München") & (stations.type == "station")]
    stations = stations.rename(columns={"latitude": "lat", "longitude": "lon", "products": "types"})
    stations = stations.filter(["name", "lat", "lon", "types"])
    stations = stations.reset_index(drop=True)
    
    mlb = sklearn.preprocessing.MultiLabelBinarizer()
    types = mlb.fit_transform(stations.types)
    stations_enc = stations.join(pd.DataFrame(types, columns=mlb.classes_)).drop(["types"], axis="columns")
    stations_enc = stations_enc.rename(columns=str.lower)
    
    return stations_enc
