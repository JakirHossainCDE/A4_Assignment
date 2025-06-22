"""
geospatial_functions.py

This script provides a collection of geospatial functions designed to interact with
OpenStreetMap data using OSMnx and visualize it interactively with Folium.
These functions are foundational for projects like "FindMyRoute," enabling the
acquisition of street networks and Points of Interest (POIs), and their
subsequent visualization on web maps.

Functions:
    - get_street_network(place_name: str, network_type: str = "walk") -> nx.MultiDiGraph:
        Downloads the street network for a specified place.
    - get_points_of_interest(place_name: str, tags: dict) -> gpd.GeoDataFrame:
        Downloads Points of Interest (POIs) based on OpenStreetMap tags.
    - calculate_graph_centroid(graph: nx.MultiDiGraph) -> tuple[float, float]:
        Calculates the geographic centroid (latitude, longitude) of a networkx graph.
    - create_interactive_map(
        graph: nx.MultiDiGraph,
        pois_gdf: gpd.GeoDataFrame,
        location_name: str,
        initial_zoom: int = 14
    ) -> folium.Map:
        Creates an interactive Folium map displaying the street network and POIs.

Dependencies:
    - osmnx: For interacting with OpenStreetMap data.
    - folium: For creating interactive Leaflet maps.
    - matplotlib: Often used by OSMnx for plotting (indirect dependency).
    - pandas: For data manipulation (GeoDataFrames are built on pandas DataFrames).
    - geopandas: For handling geospatial dataframes.
    - networkx: For graph operations on the street network.
"""

import osmnx as ox
import folium
from folium.plugins import MarkerCluster
import networkx as nx
import geopandas as gpd
from typing import Tuple

# Configure OSMnx to suppress unnecessary logging and use a cache for faster re-runs
ox.settings.log_console = False
ox.settings.use_cache = True

def get_street_network(place_name: str, network_type: str = "walk") -> nx.MultiDiGraph:
    """
    Downloads the street network for a specified place from OpenStreetMap.

    The `osmnx.graph_from_place()` function retrieves the street network
    and constructs a networkx MultiDiGraph. The 'network_type' parameter
    determines the type of network to retrieve (e.g., 'walk', 'drive', 'bike').
    'walk' includes pedestrian paths, sidewalks, and streets usable by pedestrians.

    Args:
        place_name (str): The name of the place (e.g., "Salzburg, Austria").
        network_type (str): The type of network to download (e.g., "walk", "drive").
                            Defaults to "walk".

    Returns:
        networkx.MultiDiGraph: A graph object representing the street network.

    Raises:
        ValueError: If the place_name cannot be geocoded or no network data is found.
    """
    print(f"--- Downloading street network for: {place_name} ({network_type} network) ---")
    try:
        # Download the street network graph
        G = ox.graph_from_place(place_name, network_type=network_type)
        print(f"Street network graph created with {len(G.nodes)} nodes and {len(G.edges)} edges.")
        return G
    except Exception as e:
        print(f"Error downloading street network for {place_name}: {e}")
        raise ValueError(f"Could not retrieve street network for '{place_name}'. Check place name or network type.")


def get_points_of_interest(place_name: str, tags: dict) -> gpd.GeoDataFrame:
    """
    Downloads Points of Interest (POIs) for a specified place based on OpenStreetMap tags.

    The `osmnx.features_from_place()` function allows querying various types of
    geographic features using their OSM tags. For "FindMyRoute", this is crucial
    for identifying attractions, cafes, parks, etc.

    Args:
        place_name (str): The name of the place (e.g., "Salzburg, Austria").
        tags (dict): A dictionary of OpenStreetMap tags to query (e.g.,
                     {"tourism": "attraction", "amenity": "cafe"}).

    Returns:
        geopandas.GeoDataFrame: A GeoDataFrame containing the retrieved POIs.

    Raises:
        ValueError: If no POIs are found for the given place and tags.
    """
    print(f"--- Downloading Points of Interest for: {place_name} with tags: {tags} ---")
    try:
        # Download features based on the specified place and tags
        pois = ox.features_from_place(place_name, tags)
        print(f"Found {len(pois)} POIs of various types.")

        if pois.empty:
            print(f"No POIs found for {place_name} with the given tags.")
            raise ValueError(f"No POIs found for '{place_name}' with the specified tags.")

        return pois
    except Exception as e:
        print(f"Error downloading POIs for {place_name} with tags {tags}: {e}")
        raise ValueError(f"Could not retrieve POIs for '{place_name}'. Check tags or place name.")


def calculate_graph_centroid(graph: nx.MultiDiGraph) -> Tuple[float, float]:
    """
    Calculates the geographic centroid (average latitude and longitude) of a networkx graph.

    This function extracts the 'x' (longitude) and 'y' (latitude) coordinates
    from all nodes in the graph and computes their average to find a central
    point for map display.

    Args:
        graph (networkx.MultiDiGraph): The street network graph.

    Returns:
        tuple[float, float]: A tuple containing the average latitude and longitude (lat, lon).

    Raises:
        ValueError: If the graph has no nodes.
    """
    if not graph.nodes:
        raise ValueError("Graph has no nodes to calculate a centroid.")

    node_xs = [data['x'] for node, data in graph.nodes(data=True)]
    node_ys = [data['y'] for node, data in graph.nodes(data=True)]

    latitude = sum(node_ys) / len(node_ys)
    longitude = sum(node_xs) / len(node_xs)

    return latitude, longitude


def create_interactive_map(
    graph: nx.MultiDiGraph,
    pois_gdf: gpd.GeoDataFrame,
    location_name: str,
    initial_zoom: int = 14
) -> folium.Map:
    """
    Creates an interactive Folium map displaying the street network and Points of Interest.

    The map is centered on the centroid of the street network. The street network
    is added as a GeoJSON layer, and POIs are added as markers grouped into
    MarkerClusters for better organization and performance. Different POI types
    are assigned distinct icons and colors.

    Args:
        graph (networkx.MultiDiGraph): The street network graph to display.
        pois_gdf (geopandas.GeoDataFrame): The GeoDataFrame containing POIs to display.
        location_name (str): The name of the location (e.g., "Salzburg, Austria")
                             used for map title or context.
        initial_zoom (int): The initial zoom level for the Folium map. Defaults to 14.

    Returns:
        folium.Map: An interactive Folium map object.
    """
    print(f"--- Creating interactive map for {location_name} ---")

    # Calculate map center from the graph centroid
    center_lat, center_lon = calculate_graph_centroid(graph)
    print(f"Map will be centered at: Lat {center_lat:.4f}, Lon {center_lon:.4f}")

    # Create a base Folium map
    m = folium.Map(location=[center_lat, center_lon], zoom_start=initial_zoom,
                   tiles="OpenStreetMap") # Explicitly setting tiles for clarity

    # Add the street network to the map
    print("Adding street network to map...")
    edges_gdf = ox.graph_to_gdfs(graph, nodes=False) # Get edges as GeoDataFrame
    folium.GeoJson(
        edges_gdf.__geo_interface__, # Convert GeoDataFrame to GeoJSON dictionary
        name="Street Network",
        style_function=lambda x: {
            "color": "#8b0000", # Dark red for streets
            "weight": 2,
            "opacity": 0.7,
        },
        tooltip=folium.features.GeoJsonTooltip(fields=['name'], aliases=['Street Name:'], localize=True)
    ).add_to(m)

    # Add POIs to the map using MarkerCluster for better performance with many markers
    print("Adding Points of Interest to map...")
    marker_cluster_attractions = MarkerCluster(name="Attractions").add_to(m)
    marker_cluster_cafes = MarkerCluster(name="Cafes").add_to(m)
    marker_cluster_parks = MarkerCluster(name="Parks").add_to(m)
    marker_cluster_other = MarkerCluster(name="Other POIs").add_to(m) # For any other POIs

    # Iterate through each row in the POIs GeoDataFrame and add markers
    for idx, row in pois_gdf.iterrows():
        # Ensure geometry is valid and extract coordinates
        if row['geometry'] and row['geometry'].geom_type in ['Point', 'Polygon', 'MultiPolygon']:
            try:
                # For Polygons, use the centroid; for Points, use the point itself
                lon, lat = (row['geometry'].centroid.x, row['geometry'].centroid.y) \
                           if row['geometry'].geom_type != 'Point' \
                           else (row['geometry'].x, row['geometry'].y)

                # Construct a popup message for the marker
                popup_text = f"{row.get('name', 'Unnamed POI')}"
                if row.get('tourism'): popup_text += f"Type: {row['tourism'].replace('_', ' ').title()}"
                elif row.get('amenity'): popup_text += f"Type: {row['amenity'].replace('_', ' ').title()}"
                elif row.get('leisure'): popup_text += f"Type: {row['leisure'].replace('_', ' ').title()}"
                elif row.get('shop'): popup_text += f"Type: {row['shop'].replace('_', ' ').title()}"
                # Add more types if needed

                # Assign different icon colors and names based on the POI type
                icon_color = "blue"
                icon_name = "info" # Default icon, can be changed
                add_to_cluster = marker_cluster_other # Default cluster

                if 'tourism' in row and row['tourism'] == 'attraction':
                    icon_color = "red"
                    icon_name = "star"
                    add_to_cluster = marker_cluster_attractions
                elif 'amenity' in row and row['amenity'] == 'cafe':
                    icon_color = "green"
                    icon_name = "coffee"
                    add_to_cluster = marker_cluster_cafes
                elif 'leisure' in row and row['leisure'] == 'park':
                    icon_color = "lightgreen"
                    icon_name = "tree"
                    add_to_cluster = marker_cluster_parks

                # Create a Folium Marker and add it to the appropriate cluster
                folium.Marker(
                    location=[lat, lon],
                    popup=folium.Popup(popup_text, max_width=300),
                    icon=folium.Icon(color=icon_color, icon=icon_name, prefix='fa')
                ).add_to(add_to_cluster)

            except Exception as e:
                print(f"Skipping POI '{row.get('name', 'Unnamed')}' due to geometry error: {e}")
                continue # Continue to the next POI if there's an error

    # Add a layer control to the map, allowing users to toggle different layers
    folium.LayerControl().add_to(m)

    print("Interactive map created successfully.")
    return m

# Example usage (for testing purposes, typically run from a notebook)
if __name__ == "__main__":
    place = "Salzburg, Austria"
    poi_tags = {"tourism": ["attraction", "museum"], "amenity": ["cafe", "restaurant"], "leisure": "park"}

    try:
        # Get street network
        G_salzburg = get_street_network(place)

        # Get POIs
        pois_salzburg = get_points_of_interest(place, poi_tags)

        # Create and display map (will open in a browser if run directly)
        salzburg_map = create_interactive_map(G_salzburg, pois_salzburg, place)
        salzburg_map.save("salzburg_interactive_map.html")
        print("Map saved as salzburg_interactive_map.html")

    except ValueError as ve:
        print(f"An error occurred: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
