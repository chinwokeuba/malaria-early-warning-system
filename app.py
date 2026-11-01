import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Malaria Early Warning", layout="wide")

st.title("🦟 Malaria Early Warning & Prevention  System")
st.markdown("Proactive forecast-driven risk engine for community health intervention.")

# ADD SIDEBAR SIMULATION HERE
st.sidebar.header("🎛️ Live Risk Simulation")
st.sidebar.markdown("Adjust weather metrics to test the warning engine:")
sim_rainfall = st.sidebar.slider("Rainfall (mm)", 0, 150, 65)
sim_humidity = st.sidebar.slider("Humidity (%)", 20, 100, 85)

st.sidebar.subheader("Simulation Result:")
if sim_rainfall > 70 and sim_humidity > 80:
    st.sidebar.error("🚨 Status: HIGH RISK TRIGGERED")
elif sim_rainfall > 40:
    st.sidebar.warning("⚠️ Status: HIGH RISK TRIGGERED")
elif sim_rainfall > 40:
    st.sidebar.warning("⚠️ Status: Moderate Risk")
else:
    st.sidebar.success("✅ Status: Safe Conditions")

#1. Weather forecast dataset

#function to fetch live weather from open-meteo api
def get_live_weather(lat, lon, zone_name):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,precipitation"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            current = data.get("current", {})
            return {
                "Zone": zone_name,
                "Temp_C": current.get("temperature_2m", 30),
                "Rainfall_mm": current.get("precipitation", 0),
                "Humidity": current.get("relative_humidity_2m", 70)
            }
    except Exception:
        pass

        # fallback default values if connection fails
        return {"Zone": zone_name, "Temp_C": 30, "Rainfall_mm": 5, "Humidity": 75}

        # Fetch live data
@st.cache_data(ttl=3600)
def load_forecast_data():
    zones_coords = [
        {"name": "Ibadan North", "lat": 7.4165, "lon": 3.8967},
        {"name": "Ibadan South-East", "lat": 7.3776, "lon": 3.8967},
        {"name": "Ogbomoso", "lat": 8.1333, "lon": 4.2500},
        {"name": "Challenge", "lat": 7.3667, "lon": 3.8667},
        {"name": "Bodija", "lat": 7.4250, "lon": 3.9000}
    ]
    live_data = []
    for z in zones_coords:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": z["lat"],
            "longitude": z["lon"],
            "current" : ["temperature_2m", "relative_humidity_2m"],
            "hourly": ["precipitation", "relative_humidity_2m"],
            "forecast_days": 3
        }

        zone_weather = {"Zone": z["name"], "Temp_C": 30, "Rainfall_mm": 5, "Humidity": 75}

        try:
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                current = data.get("current", {})
                hourly = data.get("hourly", {})
                rain_list = hourly.get("precipitation", [0])
                total_rain_forecast = sum(rain_list) if rain_list else 0

                zone_weather = {
                    "Zone": z["name"],
                    "Temps_C": current.get("temperature_2m",30),
                    "Rainfall_mm": round(total_rain_forecast, 1),
                    "Humidity": current.get("relative_humidity_2m", 75)
                }
        except Exception:
            pass

        live_data.append(zone_weather)

    return pd.DataFrame(live_data)
df_weather = load_forecast_data()
                                
#2. Risk evaluation logic
def assess_risk(row):
    if row['Rainfall_mm'] > 70 and row['Humidity'] > 80:
        return "High Risk (Critical Alert)"
    elif row['Rainfall_mm'] > 40:
        return "Moderate Risk"
    else:
        return"Low Risk"
        
df_weather['Risk_Level'] = df_weather.apply(assess_risk, axis=1)

# Summary Key Metrics (KPI Bar)
high_count = len(df_weather[df_weather['Risk_Level'] == "High Risk (Critical Alert)"])
mod_count = len(df_weather[df_weather['Risk_Level'] == "Moderate Risk"])
low_count = len(df_weather[df_weather['Risk_Level'] == "Low Risk"])

col1, col2, col3 = st.columns(3)
col1.metric("🚨 High Risk Zones", high_count)
col2.metric("⚠️ Moderate Risk Zones", mod_count)
col3.metric("✅ Safe Zones", low_count)

st.write("---")

# Make the table row index start from 1
df_weather.index = range(1, len(df_weather) +1)

#3. Display interactive table on the app
st.subheader("Regional Weather Forecast & Risk Status")
st.dataframe(df_weather, use_container_width=True)

#4. Filtered Alerts Section
high_risk_zones = df_weather[df_weather['Risk_Level'] == 'High Risk (Critical Alert)']

st.subheader("Actionable Dispatch Alerts")

if not high_risk_zones.empty:
    for index, row in high_risk_zones.iterrows():
        st.error(f"🚨 CRITICAL ALERT FOR: {row['Zone']}")
        st.write(f"**Trigger:** Rainfall at {row['Rainfall_mm']}mm & Humidity at {row['Humidity']}%")
        st.info("Action Required: Mobilize local sanitation teams for gutter clearing and distribute ITN bed nets immediately.")
    else:
        st.success("All zones currently within safe thresholds.")

        #5 spatial Visualization Map
st.subheader("🗺️ Regional risk Spatial View")

map_data = pd.DataFrame([
    {"name": "Ibadan North", "lat": 7.4165, "lon": 3.8967},
    {"name": "Ibadan South-East", "lat": 7.3776, "lon": 3.8967},
    {"name": "Ogbomoso", "lat": 8.1333, "lon": 4.2500},
    {"name": "Challenge", "lat": 7.3667, "lon": 3.8667},
    {"name": "Bodija", "lat": 7.4250, "lon": 3.9000}

])
st.map(map_data)

#6. Interactive zone deep-dive inspector
st.subheader("🔍 Zone Deep-Dive Inspector")
selected_zone = st.selectbox("Select a target zone to review localized health metrics:", df_weather['Zone'].unique())

#pull data for the selected zone
zone_row = df_weather[df_weather['Zone'] ==selected_zone].iloc[0]

#Display metrics in columns 
d_col1, d_col2, d_col3 = st.columns(3)
d_col1.metric("Temperature", f"{zone_row['Temps_C']} °C")
d_col2.metric("3-Day Rainfall", f"{zone_row['Rainfall_mm']} mm")
d_col3.metric("Humidity", f"{zone_row['Humidity']} %")

#status banner 
if zone_row['Risk_Level'] == 'High Risk (Critical Alert)':
    st.error(f"🚨 **CRITICAL ALERT in {selected_zone}:** High vector proliferation risk. Immediate deployment of larvicides and community sanitation required.")
elif zone_row['Risk_Level'] == 'Moderate Risk':
    st.warning(f"⚠️ **MODERATE RISK in {selected_zone}:** Monitor stagnant water accumulation and issue public safety advisories.")
else:
    st.success(f"✅ ** SAFE STATUS in {selected_zone}:** Weather parameters are currently below critical malaria transmission thresholds.")

#7. CSV Export for health dispatchers
st.subheader("📩 Export Regional Risk Report")

# Convert dataframe to CSV format
csv_data = df_weather.to_csv(index=False).encode('utf-8')

st.download_button(
    label="Download Active Risk Report (CSV)",
    data=csv_data,
    file_name="malaria_risk_dispatch_report.csv",
    mime="text/csv",
)
    