import pandas as pd
import os
import folium
import json
from folium import Element, IFrame, CssLink, JavascriptLink

base_dir = os.path.dirname(os.path.abspath(__file__))

data_dir = os.path.join(base_dir, "..", "data")
build_dir = os.path.join(base_dir, "build")

films_input_path = os.path.join(data_dir, "films.csv")
screens_input_path = os.path.join(data_dir, "screenings.csv")
search_data_path = os.path.join(base_dir, "search_data.json")

output_path = os.path.join(base_dir, "map.html")

films_df = pd.read_csv(films_input_path)
films_df["Year"] = films_df["Year"].astype("Int64")
films_df["Film ID"] = films_df["Film ID"].ffill()

screens_df = pd.read_csv(screens_input_path)

screens_df = screens_df.drop(columns=["Film Title"])

films_unique = (
    films_df.groupby("Film ID", as_index=False)
    .agg({
        "Film Title": "first",
        "Director": lambda s: s.dropna().unique().tolist()
    })
)

# Merge film metadata into the screening records
screens_films_df = screens_df.merge(
    films_unique,
    on="Film ID",
    how="left",
    validate="many_to_one"
)

def aggregate_screenings(df, group_key, coordinates_col):
    """
    Aggregate screenings by location while preserving searchable
    film metadata in separate columns.
    """

    grouped = df.groupby(group_key).agg(

        location=("Location", "first"),
        Coordinates=(coordinates_col, "first"),
        screening_count=("Film ID", "size"),
        film_ids=("Film ID", lambda s: s.dropna().unique().tolist()),
        film_titles=("Film Title", lambda s: s.dropna().unique().tolist()),
        directors=("Director", lambda s: s.dropna().explode().unique().tolist())
    )

    return grouped.reset_index()

venue_summary_df = aggregate_screenings(
    screens_films_df,
    group_key="Venue",
    coordinates_col="Coordinates"
)

#split coordinate strings into separate latitude and longitude values
venue_summary_df["Latitude"] = venue_summary_df["Coordinates"].apply(lambda x: float(x.split(",")[0].strip()))
venue_summary_df["Longitude"] = venue_summary_df["Coordinates"].apply(lambda x: float(x.split(",")[1].strip()))

search_data = venue_summary_df[
    [
        "Venue",
        "location",
        "Latitude",
        "Longitude",
        "screening_count",
        "film_ids",
        "film_titles",
        "directors"
    ]
].to_dict(orient="records")

with open(search_data_path, "w", encoding="utf-8") as f:
    json.dump(search_data, f, ensure_ascii=False, default=str, indent=2)

with open(search_data_path, "w", encoding="utf-8") as f:
    json.dump(search_data, f, ensure_ascii=False, default=str, indent=2)

m = folium.Map(location = [54.5, -3.0], zoom_start=5, tiles=None)

m.get_root().script.add_child(
    Element(
        f"window.screeningMap = {m.get_name()};"
    ),
    index=-1
)

#add satellite imagery as an alternative selectable base layer
folium.TileLayer(
    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    attr="Tiles © Esri", name="Satellite", overlay=False, control=True
).add_to(m)

for _, row in venue_summary_df.iterrows():
    marker = folium.CircleMarker(
        location=[row["Latitude"], row["Longitude"]],
        radius=4 + row["screening_count"] ** 0.5 * 2,
        tooltip=f'{row["Venue"]}',
        popup=folium.Popup(
            f"<b>{row['Venue']}</b><br>"
            f"{row['screening_count']} screenings",
            max_width=250
        ),
        color=None,
        fill=True,
        fill_color="red",
        fill_opacity=0.7
    )

    # Store the venue name as a JavaScript-readable property.
    marker.options["venueName"] = str(row["Venue"]).strip()

    marker.add_to(m)

m.get_root().html.add_child(Element("""
<div id="film-search">
    <input
        id="film-search-input"
        type="search"
        placeholder="Search films, directors, locations..."
    />
    <div id="film-search-count"></div>
</div>
"""))

#link the external CSS file containing the map styling
m.get_root().header.add_child(CssLink("static/css/map.css"))

#link the external JavaScript file controlling map interactions
m.get_root().html.add_child(JavascriptLink("static/js/map.js"))

map_variable = m.get_name()

m.get_root().html.add_child(
    Element(
        f"""
        <script>
            document.addEventListener("DOMContentLoaded", function() {{
                window.screeningMap = {map_variable};
            }});
        </script>
        """
    )
)

m.save(output_path)



