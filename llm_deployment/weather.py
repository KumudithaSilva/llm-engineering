import modal
from modal import Image

# Setup
app = modal.App("weather")
image = Image.debian_slim().pip_install("requests")


@app.function(image=image, region="eu")
def get_weather() -> str:
    import requests

    response = requests.get("https://ipinfo.io/json")

    data = response.json()
    city, region, country = data["city"], data["region"], data["country"]

    return f"Hello from {city}, {region}, {country}!!"
