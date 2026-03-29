import requests
import datetime


# Indian Soil Permeability Data

SOIL_PERMEABILITY = {
    "alluvial": "High permeability → groundwater recharge is effective.",
    "black": "Very low permeability (swelling clay) → focus on storage tanks, recharge wells.",
    "red": "Moderate permeability → both storage and recharge feasible.",
    "laterite": "Moderate to high permeability → rooftop harvesting + recharge pits.",
    "desert": "Very low natural rainfall, sandy soil → storage tanks essential.",
    "mountain": "Varied permeability, mostly shallow soil → small check dams, contour trenches."
}

ROOF_COEFFICIENTS = {
    "concrete": 0.85,
    "metal": 0.9,
    "tiles": 0.8,
    "asbestos": 0.75,
    "thatched": 0.5
}



# Fetch Rainfall Data (Current Year)

def get_rainfall_current_year(lat, lon):
    """Fetch daily rainfall for the current year till today, ignoring missing values."""
    current_year = datetime.datetime.now().year
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    start_date = f"{current_year}-01-01"

    # Archive API
    url =(
        f"https://archive-api.open-meteo.com/v1/archive?"
        f"latitude={lat}&longitude={lon}"
        f"&start_date={start_date}&end_date={today}"
        f"&daily=precipitation_sum&timezone=auto"
    )

    response = requests.get(url)
    data = response.json()

    if "daily" not in data or "precipitation_sum" not in data["daily"]:
        # fallback → Forecast API
        print(" Archive data unavailable, fetching from Forecast API instead...")
        forecast_url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}"
            f"&daily=precipitation_sum&timezone=auto&past_days=365"
        )
        response = requests.get(forecast_url)
        data = response.json()
        if "daily" not in data or "precipitation_sum" not in data["daily"]:
            raise Exception("Rainfall data not available .")

    rainfall_values = data["daily"]["precipitation_sum"]

    # Remove None values
    rainfall_values_clean = [v for v in rainfall_values if v is not None]

    return sum(rainfall_values_clean)



# Harvesting Calculation

def calculate_harvest(lat, lon, roof_area, roof_type, soil_type):
    total_rainfall_mm = get_rainfall_current_year(lat, lon)
    coefficient = ROOF_COEFFICIENTS.get(roof_type.lower(), 0.8)

    potential_harvest_litres = total_rainfall_mm * roof_area * coefficient

    # Soil recommendation
    soil_type_formatted = soil_type.title()
    soil_recommendation = SOIL_PERMEABILITY.get(
        soil_type.lower(), "Soil type not recognized, use general recharge/storage mix."
    )

    return {
        "annual_rainfall_mm": total_rainfall_mm,
        "potential_harvest_kl": round(potential_harvest_litres / 1000, 2),
        "soil_type": soil_type_formatted,
        "soil_recommendation": soil_recommendation
    }



# Example Run

# if __name__ == "__main__":
#     lat, lon = 21.1458, 79.0882
#     roof_area = 100  # m²
#     roof_type = "concrete"
#     soil_type = "black"

#     try:
#         result = calculate_harvest(lat, lon, roof_area, roof_type, soil_type)

#         print(" Rainwater Harvesting Report ")
#         print(f"Annual Rainfall (till today): {result['annual_rainfall_mm']:.2f} mm")
#         print(f"Potential Harvest: {result['potential_harvest_kl']:.2f} kilolitres/year")
#         print(f"Soil Type: {result['soil_type']}")
#         print(f"Soil Recommendation: {result['soil_recommendation']}")

    # except Exception as e:
    #     print(" Error:", e)

if __name__ == "__main__":
    try:
        # Take user input
        lat = float(input("Enter latitude: "))
        lon = float(input("Enter longitude: "))
        roof_area = float(input("Enter roof area in square meters: "))
        roof_type = input("Enter roof type (concrete/metal/tiles/asbestos/thatched): ").strip()
        soil_type = input("Enter soil type (alluvial/black/red/laterite/desert/mountain): ").strip()

        # Run calculation
        result = calculate_harvest(lat, lon, roof_area, roof_type, soil_type)

        # Display result
        print("\n Rainwater Harvesting Report 🌧")
        print(f"Annual Rainfall (till today): {result['annual_rainfall_mm']:.2f} mm")
        print(f"Potential Harvest: {result['potential_harvest_kl']:.2f} kilolitres/year")
        print(f"Soil Type: {result['soil_type']}")
        print(f"Soil Recommendation: {result['soil_recommendation']}")

    except Exception as e:
        print("Error:", e)
