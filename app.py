from helpers import *
import streamlit as st
import folium
from streamlit_folium import folium_static
from streamlit_autorefresh import st_autorefresh  
import pandas as pd

import plotly.express as px


station_info_url = "https://gbfs.lyft.com/gbfs/1.1/bos/en/station_information.json"
station_status_url = "https://gbfs.lyft.com/gbfs/1.1/bos/en/station_status.json"

st.set_page_config(page_title="Boston Bluebikes Tracker 🚲", layout="wide")


st.title("Boston Bluebikes Station Tracker 🚲")
st.markdown("Track **real-time** bike availability at each **Bluebikes** station in the Boston area.")

data_df = query_station_status(station_status_url) # Get the station status data
latlon_df = get_station_latlon(station_info_url) # Get the station latitude and longitude data
data = join_latlon(data_df, latlon_df) # Join the two data by merging on station_id
data["num_mechanical_bikes_available"] = data["num_bikes_available"] - data["num_ebikes_available"]

tab1, tab2 = st.tabs(["Station Map", "Analytics & Visualizations"])

with tab1:
    with st.container():
        st.subheader("📊 Current Station Metrics")
        column1, column2, column3 = st.columns(3)
        with column1:
            st.metric("Bikes Available Now", value = sum(data['num_mechanical_bikes_available'])) # Total number of bikes available
            st.metric("Ebikes Available Now", value = sum(data['num_ebikes_available'])) # Total number of e-bikes available

        with column2:
            st.metric("Station with Available Bikes", value = len(data.loc[(data['num_mechanical_bikes_available'] > 0)])) # Total number of stations with available bikes
            st.metric("Station with Available Ebikes", value = len(data.loc[(data['num_ebikes_available'] > 0)])) # Total number of stations with available e-bikes

        with column3:
            st.metric("Stations with Empty Docks", value = len(data.loc[(data['num_docks_available'] == 0)])) # Total number of stations with empty docks

    iamhere = None
    iamhere_return = None
    findmebike = False
    findmeadock = False
    input_bike_modes = []



    with st.sidebar:
        with st.expander("🔄 Refresh Options", expanded=True):
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
                popup=folium.Popup(f"Station: {row['name']}<br>"
                                f"Total Bikes Available: {row['num_bikes_available']}<br>"
                                f"Total Mechanical Bikes Available: {row['num_mechanical_bikes_available']}<br>"
                                f"Total Ebikes Available: {row['num_ebikes_available']}",
                                max_width=300)
            ).add_to(m)

        # Display the map in the Streamlit app
        st.subheader("Map of Stations")
        folium_static(m, width=1200, height=500)

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
                popup=folium.Popup(f"Station: {row['name']}<br>"
                                f"Total Bikes Available: {row['num_bikes_available']}<br>"
                                f"Total Docks Available: {row['num_docks_available']}", max_width=300)
            ).add_to(m)
        st.subheader("Map of Stations")
        folium_static(m, width=1200, height=500)



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
                            popup=folium.Popup(f"Station: {row['name']}<br>"
                                            f"Total Bikes Available: {row['num_bikes_available']}<br>"
                                            f"Mechanical Bikes Available: {row['num_mechanical_bikes_available']}<br>"
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
                        tooltip="Estimated walk time: {} min".format(duration),
                    ).add_to(m1)
                        
                st.subheader("Map & Route to Nearest Station")
                folium_static(m1,width=1200, height=500)
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
                        popup=folium.Popup(f"Station: {row['name']}<br>"
                                        f"Total Bikes Available: {row['num_bikes_available']}<br>"
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
                    tooltip="Estimated walk time: {} min".format(duration),
                ).add_to(m1)
            st.subheader("Map & Route to Nearest Station")
            folium_static(m1,width=1200, height=500)
            with column3:
                st.metric(label=":green[Travel Time (min)]", value=duration)

# New tab for visualizations
with tab2:

    col1, col2, col3 = st.columns(3)

    data['capacity'] = data['num_bikes_available'] + data['num_docks_available']
    data['utilization_rate'] = (data['num_bikes_available'] / data['capacity']).round(2)

    col1.metric("Total Bikes Available", data['num_bikes_available'].sum())
    col2.metric("System Utilization (Avg)", f"{data['utilization_rate'].mean():.0%}")
    col3.metric("Stations Near Capacity", f"{(data['utilization_rate'] > 0.9).mean():.0%}")

    st.subheader("Top 10 Stations with the Highest Available Bikes")
    top_stations_bikes = data.sort_values(
        by='num_bikes_available', ascending=False
    ).head(10)

    top_station = top_stations_bikes.iloc[0]


    fig_bikes = px.bar(
        top_stations_bikes,
        x='name',
        y='num_bikes_available',
        color='Bike Type' if 'Bike Type' in top_stations_bikes.columns else 'num_ebikes_available', 
        labels={
            'name': 'Station Name',
            'num_bikes_available': 'Total Bikes Available',
            'num_mechanical_bikes_available': 'Mechanical Bikes',
            'num_ebikes_available': 'E-Bikes'
        },
        title='Total Bikes Available per Station',
        hover_data=['num_bikes_available', 'num_mechanical_bikes_available', 'num_ebikes_available']
    )
    # Enhance the layout
    fig_bikes.update_layout(xaxis={'categoryorder': 'total descending'})
    st.plotly_chart(fig_bikes, use_container_width=True)

    with st.expander("Top Stations Analysis", expanded=True):
        st.success(
        f"**High Supply Hub:** The station **{top_station['name']}** currently holds the most available bikes (**{top_station['num_bikes_available']}**). This is a critical supply point for renters."
    )

        st.markdown("""
        - The top stations must be continuously monitored to for sudden drops in availability. If top bike suppliers run low, renters may face difficulties finding bikes during peak hours.
        - The large gap between the amount of mechanical bikes compared to ebikes indicates that there might be a preference for mechanical bikes among users. This insight can guide future bike procurement and distribution strategies.
            - One such strategy could be to increase the number of ebikes at high-demand stations to balance the supply and meet diverse user preferences.
            - Monitoring user feedback and usage patterns can further refine these strategies.
        """)
        st.markdown("""
        - Stations with high bike availability are likely located in areas with high demand, such as near public transit hubs, universities, or popular neighborhoods. Understanding these patterns can help optimize bike distribution and improve user satisfaction.
            - If the same stations consistently appear in the top 10, it may indicate a need for better distribution strategies to ensure bikes are available across all stations.
            - Maybe consider implementing dynamic pricing or incentives to encourage users to rent from or return to less busy stations.
                    """)


    st.divider()



    st.subheader("Distribution of Station Capacity Utilization 📈")
    fig_hist = px.histogram(
        data,
        x='utilization_rate',
        nbins=20, 
        title='Network Utilization Rate (Bikes/Capacity)',
        labels={'utilization_rate': 'Utilization Rate (0.0 = Empty to 1.0 = Full)'},
        marginal="box", 
        color_discrete_sequence=['teal']
    )
    st.plotly_chart(fig_hist, use_container_width=True)

    with st.expander("Utilization Rate Analysis", expanded=True):
        st.success("**Optimal Utilization Range:** Most stations should cluster around 0.4–0.7 utilization, meaning neither too empty nor too full.")
        st.markdown("""
        - Stations who stay near 0.0 utilization are at high risk of running out of bikes, leading to customer dissatisfaction and lost rentals.
        - Stations who stay near 1.0 utilization are at high risk of being unable to accept returned bikes, causing inconvenience to the customers.
             - To recognize these patterns, try to implement a threshold system that flags stations that consistently fall outside the optimal range.
             """)
        st.markdown("""
        - If the distribution is consistently skewed towards either extreme, it may indicate systemic issues in bike distribution or station placement.
            - Regularly review and adjust bike allocation strategies based on real-time data to maintain balanced utilization.
            - Consider expanding stations into underserved neighborhoods or areas with growing demand.
        """)
    st.divider()

    st.subheader("Station Capacity vs Utilization Rate")
    fig_scatter = px.scatter(
        data,
        x='capacity',
        y='utilization_rate',
        size='capacity',
        color='utilization_rate',
        hover_name='name',
        title='Station Capacity vs Utilization Rate',
        labels={'capacity': 'Station Capacity', 'utilization_rate': 'Utilization Rate (0.0 = Empty to 1.0 = Full)'},
        color_continuous_scale=px.colors.sequential.Viridis
    )

    fig_scatter.add_hline(y=0.95, line_dash='dash', line_color='red',
                        annotation_text='Near Full (High Return Risk)',
                        annotation_position='bottom right')
    fig_scatter.add_hline(y=0.05, line_dash='dash', line_color='orange',
                        annotation_text='Near Empty (High Rent Risk)',
                        annotation_position='top right')
    
    fig_scatter.update_layout(
        height=500,
        xaxis_title="Total Capacity",
        yaxis_title="Current Utilization Rate",
        yaxis_tickformat=".0%"  # Format y-axis as percentage
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    with st.expander("Capacity vs Utilization Analysis", expanded=True):
        st.success("**Capacity Impact on Utilization:** Larger stations tend to have more stable utilization rates, while smaller stations are more volatile.")
        st.markdown("""
        - **Bottom Right Quadrant (High Capacity, Low Utilization):** These stations have a large capacity but low bike availability. This could indicate that the station has too many docks or under-utilization of bikes. The goal here should be to move bikes back into these stations to increase utilization to a healthier level.
        - **Top Left Quadrant (Low Capacity, High Utilization):** These stations have a small capacity but high bike availability. This could indicate that these stations are in high-demand areas. Consider expanding these stations to accommodate more bikes and reduce the risk of running out.
        - Smaller stations (low capacity) are more likely to experience extreme utilization rates (either very high or very low). This is because a small change in the number of bikes can significantly impact the utilization rate. For example, if a station has a capacity of 10 and 9 bikes are rented out, the utilization rate drops to 0.1 (10%). In contrast, a larger station with a capacity of 100 would only see a drop to 0.91 (91%) if 9 bikes were rented out.
            - Monitor smaller stations with **real-time rebalancing** to be prepared for sudden changes in demand.
        """)
