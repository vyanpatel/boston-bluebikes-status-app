# Boston Bluebikes Station Tracker 🚲

A real-time dashboard tracking bike availability across Boston's Bluebikes bike-sharing system. Built with Streamlit and Python, this app helps users find available bikes and docks across the city.

## Features

- **Real-time Tracking:** Auto-refreshes every 30 seconds to show current bike and dock availability
- **Interactive Maps:** Visual representation of all Bluebike stations in the Boston area with color-coded availability 
- **Smart Search:** 
  - Find nearest available bikes (regular or e-bikes)
  - Locate nearest available docks for returns
  - Walking directions with estimated travel time
- **System Stats:** 
  - Total bikes and e-bikes available
  - Active station counts
  - Dock availability

## Technologies Used

### Data Processing
- **Pandas** - Data manipulation and analysis
- **JSON** - Data format parsing
- **urllib** - URL handling and requests
- **datetime** - Time series handling

### Geospatial Tools
- **GeoPy** 
  - Distance calculations (geodesic)
  - Geocoding (Nominatim)
- **OSRM** (OpenStreetMap Routing Machine)
  - Route calculations
  - Walking directions
  - Duration estimates



### APIs
1. **Bluebikes GBFS Boston (General Bikeshare Feed Specification)**
   - Station Information
   - Real-time station status
   - Bike availability data

2. **Nominatim Geocoding API**
   - Address to coordinate conversion
   - Reverse geocoding capabilities

3. **OpenStreetMap Routing Machine (OSRM)**
   - Walking routes
   - Distance calculations
   - Turn-by-turn directions
  
### Development Tools
- **Python** - Core programming language
- **Conda** - Environment management

## Getting Started

1. Clone the repository
```bash
git clone https://github.com/vyanpatel/boston-bluebikes-status-app.git
```

2. Create conda environment
```bash
conda create --name bluebikes_streamlit
conda activate bluebikes_streamlit
```
3. Install pip if it is not in the conda environment
   ```bash
   pip --version
   conda install pip
   ```
4. Install the requirements into the conda environment
   ```bash
   pip install -r requirements.txt
6. Run the app
```bash
streamlit run app.py
```

## Live Demo

https://boston-bluebikes-tracker-app.streamlit.app/

## Data Source
**Bluebikes GBFS API**
  - Update frequency: 30 seconds
  - Data format: JSON
   - Station Information: `https://gbfs.lyft.com/gbfs/1.1/bos/en/station_information.json`
   - Station Status: `https://gbfs.lyft.com/gbfs/1.1/bos/en/station_status.json`
