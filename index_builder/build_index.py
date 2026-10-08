import os
import pandas as pd
from render_index import render_index_sections, render_page
from index_helpers import (
    group_items_alphabetically,
    build_search_index
    )

single_fields = {
    "Film Title": "film_title",
    "Year": "year",
    "IMDB": "imdb",
    "Subtitles": "subtitles"
}

multi_fields = {
    "Director": "directors",
    "Country": "countries",
    "Language": "languages",
}

base_dir = os.path.dirname(os.path.abspath(__file__))

data_dir = os.path.join(base_dir, "..", "data")
input_path = os.path.join(data_dir, "films.csv")

build_dir = os.path.join(base_dir, "build")
output_path = os.path.join(build_dir, f"film_index.html")

os.makedirs(os.path.join(build_dir), exist_ok=True)

df = pd.read_csv(input_path)
df["Year"] = df["Year"].astype("Int64")

df["Film ID"] = df["Film ID"].ffill()

films = []

for film_id, group in df.groupby("Film ID", sort=False):

    film = {}

    film["film_id"] = film_id 

    for column, json_name in single_fields.items():
        values = group[column].dropna()

        if len(values) > 0:
            film[json_name] = values.iloc[0]

    for column, json_name in multi_fields.items():
        values = group[column].dropna().unique().tolist()
        film[json_name] = values

    films.append(film)

films_alpha = group_items_alphabetically(films)

body_html = render_index_sections(films_alpha)

#create the title for the entity index page
film_index_title = "Film Index"
film_index_html = render_page(film_index_title, body_html)

#write the generated index page to the build directory
with open(output_path, "w", encoding="utf-8") as f:
    f.write("\n".join(film_index_html))
    print(f"Index built in {output_path}")

#build the JSON search index
build_search_index(films, build_dir)



