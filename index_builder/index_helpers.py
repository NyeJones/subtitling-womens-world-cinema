import os
import json
from collections import defaultdict
from unidecode import unidecode

def normalize_for_sort(text):
    """
    Normalize text for alphabetical sorting.

    Args:
        text (str): Text to normalize.

    Returns:
        str:
            Lowercase ASCII transliteration of the input text, or an
            empty string if no text is provided.
    """
    if not text:
        return ""
    return unidecode(text).lower()

def group_items_alphabetically(film_data):
    """
    Group entity items alphabetically by their preferred name.

    Names are normalized before determining the grouping letter and sorting
    items, allowing names with diacritics to be grouped consistently.

    Args:
        items (list): List of extracted entity data dictionaries.

    Returns:
        dict:
            Dictionary mapping alphabetical grouping letters to sorted
            lists of entity items. Items without a name are grouped under
            "#".
    """
    
    #create a dictionary where each grouping letter maps to a list of items
    grouped = defaultdict(list)

    #determine the grouping letter for each item from its preferred name
    for film_id, item_data in film_data.items():
        name = item_data.get("film_title")

        item_data["film_id"] = film_id

        if name:
            normalized = normalize_for_sort(name)

            #ignore a leading exclamation mark when choosing the group.
            normalized = normalized.lstrip("!")

            #group alphabetically, or under "#" if the title starts with a number
            #or another non-alphabetic character.
            first_letter = (
                normalized[0].upper()
                if normalized and normalized[0].isalpha()
                else "#"
            )
        else:
            #items without a preferred name are grouped under "#"
            first_letter = "#"

        grouped[first_letter].append(item_data)

    #sort items within each alphabetical group using normalized names
    for letter in grouped:
        grouped[letter].sort(
            key=lambda x: normalize_for_sort(x["film_title"][0]) if x.get("film_title") else ""
        )

    #sort the grouping letters themselves before returning the dictionary
    return dict(sorted(grouped.items()))

def build_search_index(film_data, build_dir):
    
    records = []

    for film_id, item_data in film_data.items():

        title = item_data.get("film_title")

        directors = item_data.get("directors", [])

        #create the fields common to every search record
        record = {
            "id": film_id,
            "title": title,
            "directors": directors,
            "url": f"indexes/film_index.html#{film_id}"
        }

        records.append(record)

    output_path = os.path.join(build_dir, "search_index.json")

    #write all records to JSON
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

