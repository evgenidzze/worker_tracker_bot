import requests

from config import API_MAP


def get_static_map_image(latitude, longitude, zoom=16, size="600x400"):
    base_url = "https://maps.googleapis.com/maps/api/staticmap"
    marker_params = f"markers=color:red|label:|{latitude},{longitude}"
    params = {
        "center": f"{latitude},{longitude}",
        "zoom": zoom,
        "size": size,
        "markers": marker_params,
        "key": API_MAP,
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        image_data = response.content
        return image_data
    else:
        print("Error:", response.status_code)
