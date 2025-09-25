# Boston Bluebikes Station Tracker 🚲

A real-time dashboard tracking bike availability across Boston's Bluebikes bike-sharing system. Built with Streamlit and Python, this app helps users find available bikes and docks across the city.

## Features

- **Real-time Tracking:** Auto-refreshes every 30 seconds to show current bike availability
- **Interactive Maps:** Visual representation of all Bluebike stations with color-coded availability
- **Smart Search:** 
  - Find nearest available bikes (regular or e-bikes)
  - Locate available docks for returns
  - Walking directions with estimated travel time
- **System Stats:** 
  - Total bikes and e-bikes available
  - Active station counts
  - Dock availability

## Technologies Used

- Python 3.8
- Streamlit
- Folium (mapping)
- GBFS (General Bikeshare Feed Specification)
- OpenStreetMap Routing Machine (OSRM)

## Getting Started

1. Clone the repository
```bash
git clone [your-repo-url]
```

2. Create conda environment
```bash
conda env create -f environment.yml
conda activate bluebikes_streamlit
```

3. Run the app
```bash
streamlit run app.py
```

## Live Demo

[Add your deployed app URL here]

## Data Source

**Bluebikes GBFS API**
   - Station Information: `https://gbfs.lyft.com/gbfs/1.1/bos/en/station_information.json`
   - Station Status: `https://gbfs.lyft.com/gbfs/1.1/bos/en/station_status.json`

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

