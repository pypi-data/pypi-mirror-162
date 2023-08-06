from zipfile import ZipFile

import geojson
import requests


def _dnk_download(filename="no_zone.Denmark.zip"):
    """Download Danish No-Fly Zones From droneluftrum.dk

    Args:
        filename (str, optional): Defaults to "no_zone.Denmark.zip".
    """
    url = "https://st1frontendutmdroneprd.blob.core.windows.net/geojson/geojson.zip"
    response = requests.request("GET", url)
    with open(filename, 'wb') as f:
        f.write(response.content)
    return filename


def get_no_fly(country="DNK"):
    """Get no-fly zones for a country.

    Args:
        country (str, optional): ISO 3166 alpha-3 country code. Defaults to 
            Denmark i.e. "DNK".

    Raises:
        KeyError: When country code isn't implemented.

    Returns:
        {'zone_name': {geojson FeatureCollection}}: Dictionary of various 
            geojson FeatureCollections.
    """
    # TODO (2) Proper caching
    import os
    filename = None
    if country == "DNK":
        if os.path.isfile("./no_zone.Denmark.zip"): # Check if file exists
            filename="no_zone.Denmark.zip"
        else:
            filename = _dnk_download()
    else:
        raise KeyError(f"Country {country} not found.")

    no_zones = {}
    with ZipFile(filename, 'r') as zip:
        for info in zip.infolist():
            if not info.filename.endswith('.geojson'): # Skip non geojson
                continue
            no_zones[info.filename] = geojson.loads(zip.read(info.filename))
    return no_zones


if __name__ == "__main__":
    print("Downloading no-fly zones...")
    no_zones = get_no_fly()
