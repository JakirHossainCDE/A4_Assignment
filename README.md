# Assignment A4 – Geospatial Python Libraries: OSMnx and Folium with Modular Functions  
**By Jakir Hossain**

---

## 📌 Overview

This notebook demonstrates the use of a modular Python script (`geospatial_functions.py`) which encapsulates functions for using two crucial geospatial Python libraries: **OSMnx** and **Folium**. This approach promotes **code reusability, readability**, and **maintainability**, which are essential for developing robust applications like our **"FindMyRoute: Discover the Optimised Tourist Path for Your City"** project.

The external Python file provides the core functionalities of data acquisition (road networks and Points of Interest) and interactive map visualization, centralizing these operations into well-defined functions.

### 🎯 Objectives

- Demonstrate the proper use of script and function docstrings in a Python file.
- Show how to import and utilize custom geospatial functions from an external `.py` file.
- Acquire street network and Points of Interest (POIs) data for **Salzburg, Austria**, using OSMnx via the imported functions.
- Visualize the acquired street networks and POIs on an interactive **Folium** map using the imported functions.

---

## 🧰 Libraries Used

The core libraries used by the functions are:

- **OSMnx**: For downloading, constructing, analyzing, and visualizing street networks and other geospatial data from OpenStreetMap.
- **Folium**: For creating interactive Leaflet maps in Python.
- **GeoPandas**: For handling geospatial dataframes (used by OSMnx for features).
- **NetworkX**: For working with graph objects (used by OSMnx for street networks).

---

## ⚙️ Installation

First, ensure you have the necessary libraries installed. Run the following command in your terminal or a notebook cell:

```bash
pip install osmnx folium matplotlib geopandas networkx


🧪 Part 1: Setting up the Environment and Importing Functions
We start by importing the necessary functions from our geospatial_functions.py script. Ensure that geospatial_functions.py is in the same directory as this notebook or accessible via your Python path.

import pandas as pd
import folium
import networkx as nx
import geopandas as gpd

from geospatial_functions import (
    get_street_network,
    get_points_of_interest,
    create_interactive_map,
    calculate_graph_centroid
)

print("Custom geospatial functions imported successfully!")


🌍 Part 2: Data Acquisition with OSMnx Using Imported Functions
We'll now use the get_street_network and get_points_of_interest functions to acquire data for Salzburg, Austria. This keeps our notebook clean and focuses on the workflow.

place_name = "Salzburg, Austria"
print(f"\n--- Starting Data Acquisition for: {place_name} ---")

# --- 1. Download Street Network ---
try:
    salzburg_graph = get_street_network(place_name, network_type="walk")
except ValueError as e:
    print(f"Failed to get street network: {e}")
    salzburg_graph = None


🧭 Define Points of Interest (POIs) to Download

poi_tags = {
    "tourism": ["attraction", "museum", "artwork"],
    "amenity": ["cafe", "restaurant", "pub", "bar"],
    "leisure": ["park", "garden", "playground"],
    "shop": ["books", "souvenirs"]
}

try:
    salzburg_pois = get_points_of_interest(place_name, poi_tags)
except ValueError as e:
    print(f"Failed to get POIs: {e}")
    salzburg_pois = None

🗃️ Display POIs Sample

if salzburg_pois is not None and not salzburg_pois.empty:
    print("\nSample of POIs GeoDataFrame (first 5 rows and relevant columns):")
    display_cols = [col for col in ['name', 'geometry', 'amenity', 'tourism', 'leisure', 'shop'] if col in salzburg_pois.columns]
    print(salzburg_pois[display_cols].head())
else:
    print("\nNo POIs data available for display.")

print("\n--- Data Acquisition Complete ---")


🗺️ Part 3: Visualization with Folium Using Imported Function
We'll now use create_interactive_map to generate an interactive map displaying the street network and categorized POIs.

print("\n--- Starting Folium Map Visualization ---")

if salzburg_graph is not None and salzburg_pois is not None and not salzburg_pois.empty:
    try:
        salzburg_interactive_map = create_interactive_map(
            graph=salzburg_graph,
            pois_gdf=salzburg_pois,
            location_name=place_name,
            initial_zoom=14
        )

        print("\nMap is ready to be displayed below.")
        salzburg_interactive_map
    except ValueError as e:
        print(f"Failed to create map: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during map creation: {e}")
else:
    print("\nCannot create map: Either street network or POIs data is missing or empty.")

print("\n--- Folium Map Visualization Complete ---")

✅ Conclusion
This notebook successfully demonstrates a modular approach to geospatial data acquisition and visualization using OSMnx and Folium.
