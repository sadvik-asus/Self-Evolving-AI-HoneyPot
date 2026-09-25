import requests

def get_geo_data(ip_address):
    """
    Fetches geographic data for a given IP address using the free ip-api.com service.
    Note: Free tier has a rate limit of 45 requests per minute.
    """
    if ip_address in ["127.0.0.1", "::1", "localhost"]:
        return {
            "country": "Localhost",
            "city": "Localhost",
            "lat": 0.0,
            "lon": 0.0,
            "isp": "Local Development"
        }
        
    try:
        response = requests.get(f"http://ip-api.com/json/{ip_address}?fields=status,message,country,city,lat,lon,isp")
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") == "success":
            return {
                "country": data.get("country"),
                "city": data.get("city"),
                "lat": data.get("lat"),
                "lon": data.get("lon"),
                "isp": data.get("isp")
            }
        else:
            print(f"GeoIP Error: {data.get('message')}")
            return None
    except Exception as e:
        print(f"Failed to fetch GeoIP data: {e}")
        return None

if __name__ == "__main__":
    # Test with Google's DNS
    print(get_geo_data("8.8.8.8"))
