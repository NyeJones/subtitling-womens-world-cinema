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

def group_items_alphabetically(items):
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
    for item in items:
        name_list = item.get("film_title")

        if name_list:
            name = name_list[0]
            normalized = normalize_for_sort(name)

            #use "#" for names that cannot produce a grouping letter
            first_letter = normalized[0].upper() if normalized else "#"
        else:
            #items without a preferred name are grouped under "#"
            first_letter = "#"

        grouped[first_letter].append(item)

    #sort items within each alphabetical group using normalized names
    for letter in grouped:
        grouped[letter].sort(
            key=lambda x: normalize_for_sort(x["film_title"][0]) if x.get("film_title") else ""
        )

    #sort the grouping letters themselves before returning the dictionary
    return dict(sorted(grouped.items()))

def build_search_index(items, build_dir):
    
    records = []

    for item_data in items:

        identifier = item_data.get("film_id")
        if not identifier:
            continue 

        title = item_data.get("film_title")

        directors = item_data.get("directors", [])

        #create the fields common to every search record
        record = {
            "id": identifier,
            "title": title,
            "directors": directors,
            "url": f"indexes/film_index.html#{identifier}"
        }

        records.append(record)

    output_path = os.path.join(build_dir, "search_index.json")

    #write all records to JSON
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

