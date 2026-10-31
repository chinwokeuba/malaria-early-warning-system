import streamlit as st
import pandas as pd

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

#1. Weather forecast dadset
data = {
    'Zone': ['Ibadan North', 'Ibadan South-East', 'Ogbomoso', 'Challenge', 'Bodija'],
    'Temp_C': [32, 29, 34, 30, 28],
    'Rainfall_mm': [45, 85, 20, 60, 15],
    'Humidity': [82, 88, 70, 85, 65]
}

df_weather = pd.DataFrame(data)

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
