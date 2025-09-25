from helpers import *
import streamlit as st
import folium
from streamlit_folium import folium_static
from streamlit_autorefresh import st_autorefresh  


station_info_url = "https://gbfs.lyft.com/gbfs/1.1/bos/en/station_information.json"
station_status_url = "https://gbfs.lyft.com/gbfs/1.1/bos/en/station_status.json"

st.title("Boston Bluebikes Station Tracker")
st.markdown("This dashboard tracks bike availability at each Bluebikes station in the Boston area.")

data_df = query_station_status(station_status_url) # Get the station status data
latlon_df = get_station_latlon(station_info_url) # Get the station latitude and longitude data
data = join_latlon(data_df, latlon_df) # Join the two data by merging on station_id

column1, column2, column3 = st.columns(3)
with column1:
    st.metric("Bikes Available Now", value = sum(data['num_bikes_available'])) # Total number of bikes available
    st.metric("Ebikes Available Now", value = sum(data['num_ebikes_available'])) # Total number of e-bikes available

with column2:
    st.metric("Station with Available Bikes", value = len(data.loc[(data['num_bikes_available'] > 0)])) # Total number of stations with available bikes
    st.metric("Station with Available Ebikes", value = len(data.loc[(data['num_ebikes_available'] > 0)])) # Total number of stations with available e-bikes

with column3:
    st.metric("Stations with Empty Docks", value = len(data.loc[(data['num_docks_available'] == 0)])) # Total number of stations with empty docks

iamhere = None
iamhere_return = None
findmebike = False
findmeadock = False
input_bike_modes = []



with st.sidebar:
    st.subheader("Refresh")
    auto = st.toggle("Auto-refresh every 30s", value=True)
    if st.button("Refresh Now"):
        st.cache_data.clear()
        st.rerun()
    st.divider()
    bike_method = st.selectbox("Are you looking to rent or return a bike?", ['Rent', 'Return']) # Select bike mode(s) to display on map
    if bike_method == 'Rent':
        input_bike_modes = st.multiselect("Select bike types to rent:", ['Ebike', 'Mechanical'])
        input_bike_modes = [item.lower() for item in input_bike_modes]
        st.header("Where are you located?")
        input_street = st.text_input("Street Address", value="") # Input street address
        input_city = st.text_input("City", value="Boston") # Input city
        input_state = st.text_input("State", value="MA") # Input state
        findmebike = st.button("Find me a bike!", type="primary") # Button to find a bike

        if findmebike:
            if input_street != "":
                iamhere = geocode(input_street + ", " + input_city + ", " + input_state) # Geocode the full address
                if iamhere == "":
                    st.error("Please enter a valid address.")
            else:
                st.error("Please enter a street address") # Error message if street address is empty 
    elif bike_method == 'Return':
        st.subheader("Where are you located?")
        input_street = st.text_input("Street Address", value="") # Input street address
        input_city = st.text_input("City", value="Boston") # Input city
        input_state = st.text_input("State", value="MA") # Input state
        findmeadock = st.button("Find me a dock!", type="primary") 
        if findmeadock:
            if input_street != "":
                iamhere_return = geocode(input_street + ", " + input_city + ", " + input_state) 
                if iamhere_return == '':
                    st.error("Please enter a valid address.")
            else:
                st.error("Please enter a valid street address") 
if auto:
    st_autorefresh(interval=30_000, key="bb-autorefresh")  # Auto-refresh every 30 seconds
# Create a map centered around Boston
if bike_method == "Rent" and findmebike == False:
    center = [42.3601, -71.0589]
    m = folium.Map(location=center, zoom_start=13, tiles='cartodbpositron')
    for _, row in data.iterrows():
        marker_color = get_marker_color(row['num_bikes_available'])
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=2,
            color=marker_color,
            fill=True,
            fill_color=marker_color,
            fill_opacity=0.7,
            popup=folium.Popup(f"Station ID: {row['station_id']}<br>"
                            f"Total Bikes Available: {row['num_bikes_available'] + row['num_ebikes_available']}<br>"
                            f"Total Mechanical Bikes Available: {row['num_bikes_available']}<br>"
                            f"Total Ebikes Available: {row['num_ebikes_available']}",
                            max_width=300)
        ).add_to(m)

    # Display the map in the Streamlit app
    folium_static(m)

if bike_method == "Return" and findmeadock == False:
    center = [42.3601, -71.0589]
    m = folium.Map(location=center, zoom_start=13, tiles='cartodbpositron')  # Create a map with a grey background
    for _, row in data.iterrows():
        marker_color = get_marker_color(row['num_docks_available'])  # Determine marker color based on bikes available
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=2,
            color=marker_color,
            fill=True,
            fill_color=marker_color,
            fill_opacity=0.7,
            popup=folium.Popup(f"Station ID: {row['station_id']}<br>"
                               f"Total Bikes Available: {row['num_bikes_available'] + row['num_ebikes_available']}<br>"
                               f"Total Docks Available: {row['num_docks_available']}", max_width=300)
        ).add_to(m)
    folium_static(m)



if findmebike:
    if input_street != "" and iamhere is not None and iamhere != "":
        try:
            chosen_station = get_bike_availability(iamhere, data, input_bike_modes)
            if chosen_station is None:
                st.error("No stations found with available bikes matching your criteria.")
                st.stop() 

            center = iamhere
            m1 = folium.Map(location=center, zoom_start=16, tiles='cartodbpositron')
            for _, row in data.iterrows():
                    marker_color = get_marker_color(row['num_bikes_available'])  # Determine marker color based on bikes available
                    folium.CircleMarker(
                        location=[row['lat'], row['lon']],
                        radius=2,
                        color=marker_color,
                        fill=True,
                        fill_color=marker_color,
                        fill_opacity=0.7,
                        popup=folium.Popup(f"Station ID: {row['station_id']}<br>"
                                        f"Total Bikes Available: {row['num_bikes_available'] + row['num_ebikes_available']}<br>"
                                        f"Mechanical Bikes Available: {row['num_bikes_available']}<br>"
                                        f"Ebikes Available: {row['num_ebikes_available']}", max_width=300)
                    
                    ).add_to(m1)
            folium.Marker(location=(chosen_station[1], chosen_station[2]),
                            popup=folium.Popup(f"Mechanical Bikes Available: {chosen_station[3]}<br>"
                                            f"Ebikes Available: {chosen_station[4]}", max_width=300),
                            icon=folium.Icon(color="red", icon="bicycle", prefix="fa")
                    ).add_to(m1)
            folium.Marker(
                    location=iamhere,
                    popup="You are here.",
                    icon=folium.Icon(color="blue", icon="person", prefix="fa")
                ).add_to(m1)
            coordinates, duration = run_osrm(chosen_station, iamhere)  # Get route coordinates and duration
            folium.PolyLine(
                    locations=coordinates,
                    color="blue",
                    weight=5,
                    tooltip="it'll take you {} to get here.".format(duration),
                ).add_to(m1)
                    
            folium_static(m1)
            with column3:
                st.metric(label=":green[Travel Time (min)]", value=duration)
        except Exception as e:
            st.error(f"Error finding available bikes: {str(e)}")
            st.stop()
#Find me a dock
if findmeadock:
    if input_street != "" and iamhere_return is not None and iamhere_return != "":
        chosen_station = get_dock_availability(iamhere_return, data)
        center = iamhere_return
        m1 = folium.Map(location=center, zoom_start=16, tiles='cartodbpositron')
        for _, row in data.iterrows():
            marker_color = get_marker_color(row['num_docks_available'])  
            folium.CircleMarker(
                    location=[row['lat'], row['lon']],
                    radius=2,
                    color=marker_color,
                    fill=True,
                    fill_color=marker_color,
                    fill_opacity=0.7,
                    popup=folium.Popup(f"Station ID: {row['station_id']}<br>"
                                       f"Total Bikes Available: {row['num_bikes_available'] + row['num_ebikes_available']}<br>"
                                       f"Total Docks Available: {row['num_docks_available']}", max_width=300)
                ).add_to(m1)
        folium.Marker(
            location=iamhere_return,
            popup="You are here.",
            icon=folium.Icon(color="blue", icon="person", prefix="fa")
        ).add_to(m1)
        folium.Marker(location=(chosen_station[1], chosen_station[2]),
                          popup=f"Number of Docks Available: {data.loc[data['station_id'] == chosen_station[0], 'num_docks_available'].values[0]}",
                          icon=folium.Icon(color="red", icon="bicycle", prefix="fa")
                          ).add_to(m1)
        coordinates, duration = run_osrm(chosen_station, iamhere_return)
        folium.PolyLine(
                locations=coordinates,
                color="blue",
                weight=5,
                tooltip="it'll take you {} to get here.".format(duration),
            ).add_to(m1)
        folium_static(m1)
        with column3:
            st.metric(label=":green[Travel Time (min)]", value=duration)