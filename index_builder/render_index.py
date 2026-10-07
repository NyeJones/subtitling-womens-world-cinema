import string
import html
import re
from index_helpers import normalize_for_sort

def render_alphabet_nav():
    """
    Render an alphabetical navigation bar (A–Z).

    Returns:
        list[str]: A list of HTML strings representing a navigation
        element containing buttons for each uppercase letter.
    """
    html = ["  <div class='alphabet mb-3 d-flex flex-wrap gap-2' id='alphabet-nav'>"]
    for letter in string.ascii_uppercase:
        html.append(f"    <button class='btn btn-sm btn-outline-secondary alphabet-btn' data-letter='{letter}'>{letter}</button>")
    html.append("   <button type='button' class='btn btn-sm btn-outline-primary show-all alphabet-btn' data-letter='all'>Show All</button>")
    html.append("  </div>")
    return html

def render_search():
    """
    Render a search box with a clear button for the index.

    Returns:
        list[str]: HTML lines for a search form.
    """
    html = [
        "  <form id='index-search-form' class='d-flex mt-3 mt-md-0 index-search-form' onsubmit='return false;'>",
        "    <div class='input-group input-group-sm search-group'>",
        "      <input type='text' id='index-search' class='search-input form-control' placeholder='Search by name, diacritics ignored..' autocomplete='off'>",
        "      <button type='button' id='search-clear' class='btn btn-secondary search-button search-clear-btn'>Clear</button>",
        "    </div>",
        "  </form>"
    ]
    return html

def first(lst):
    """Return the first item of a list or None if empty."""
    return lst[0] if lst else None


def esc(value):
    """Escape a string for safe HTML insertion."""
    return html.escape(str(value)) if value else ""

def render_list(items, css_class=None):
    """
    Sort and render a list of items as a vertical block using <div> for each item.

    Parameters:
        items (list[str]): The items to render.
        css_class (str, optional): CSS class applied to each <div> item.

    Returns:
        str: HTML string for the list, or empty string if no items.
    """
    if not items:
        return ''

    #sort displayed values consistently using normalization function
    items = sorted(items, key=normalize_for_sort)

    cls_attr = f' class="{esc(css_class)}"' if css_class else ''
    
    html = []
    for item in items:
        html.append(f"<div{cls_attr}>{esc(item)}</div>")

    return '\n'.join(html)

def render_entry_header(identifier, title):
    """
    Render the standard header for an index entry.

    The header displays the entity title, if present, and entity identifier, 
    followed by a toggle button used to show or hide the entry details.

    Parameters:
        identifier (str): Unique identifier for the entity.
        title (str): Display title for the entity.

    Returns:
        str: HTML string containing the entry header.
    """
    html = ["<div class='entry-header'>"]

    #display the title when available, otherwise use unique identifier
    if title:
        html.append(f"<span class='entry-title'>{esc(title)}</span>")
        html.append(f"<span class='entry-id'>({esc(identifier)})</span>")
    else:
        html.append(f"<span class='entry-title'>{esc(identifier)}</span>")

    html.append("  <button class='toggle' aria-label='Show details'>▸</button>")
    html.append("</div>")

    return "\n".join(html)

def make_entity_url(entity_type, key, single_page=True):
    """
    Build an internal URL for an entity index entry.

    Parameters:
        entity_type (str): Type of entity being linked to, e.g. person or place.
        key (str): XML identifier of the entity.
        single_page (bool): If True, link to the entity anchor on the current
            page; otherwise link to the entity's separate index page.

    Returns:
        str: URL pointing to the entity index entry.
    """
    #use a local anchor when all entity types are displayed on the same page
    if single_page:
        return f"#{esc(key)}"
    #otherwise link to the separate index page for the entity type
    return f"{entity_type}_index.html#{esc(key)}"

def html_renderer(item_data):

    html = []
    
    #basic entry information used for the index heading and anchor
    identifier = item_data.get("film_id")
    title = item_data.get("film_title")

    html.append(f"<div class='index-entry' id='{esc(item_data)}'>")
    
    #render the standard entry heading and details container
    html.append(render_entry_header(identifier, title))
    html.append("<div class='item-details'>")

    #render directors when available
    directors_html = render_list(item_data.get("directors"), "item-name")
    
    if directors_html:
        html.append("<div class='entry-block entry-directors'>")
        html.append("<span class='subheading'>Director(s)</span>")
        html.append(directors_html)
        html.append("</div>")

    #render year when value available
    year = item_data.get("year")
    
    if year:
        html.append("<div class='entry-block entry-year'>")
        html.append("<span class='subheading'>Year</span>")
        html.append(f"<span class='item-name'>{esc(year)}</span>")
        html.append("</div>")

    #render countries when available
    countries_html = render_list(item_data.get("countries"), "item-name")
    
    if countries_html:
        html.append("<div class='entry-block entry-countries'>")
        html.append("<span class='subheading'>Country(s)</span>")
        html.append(countries_html)
        html.append("</div>")

    #render languages when available
    languages_html = render_list(item_data.get("languages"), "item-name")
    
    if languages_html:
        html.append("<div class='entry-block entry-languages'>")
        html.append("<span class='subheading'>Language(s)</span>")
        html.append(languages_html)
        html.append("</div>")

    #render imdb when value available
    imdb_id = item_data.get("imdb")
    imdb = f"https://www.imdb.com/title/{imdb_id}"
    
    if imdb:
        html.append("<div class='entry-block entry-imdb'>")
        html.append("<span class='subheading'>IMDB</span>")
        html.append(f"<a href='{esc(imdb)}' target='_blank' class='item-name'>{esc(imdb)}</a>")
        html.append("</div>")

    #render subtitles when value available
    subtitles = item_data.get("subtitles")
    
    if subtitles:
        html.append("<div class='entry-block entry-subtitles'>")
        html.append("<span class='subheading'>Subtitles</span>")
        html.append(f"<span class='item-name'>{esc(subtitles)}</span>")
        html.append("</div>")

    html.append("</div>")
    return "\n".join(html)


def render_index_sections(items_by_letter):
    """
    Render grouped entity entries as a single index list.

    Iterates through the alphabet in order and uses the entity type to
    dispatch each item to its corresponding renderer.

    Args:
        items_by_letter (dict): Entity entries grouped by initial letter.
        entity_tag (str): Entity type used to select the appropriate renderer.

    Returns:
        str: HTML string containing the complete index list.
    """

    html = []
    
    #use a single list container for all entries
    html.append("<ul class='index-list list-unstyled' id='all-entries'>")

    #iterate through the alphabet in order so that entries remain grouped
    #according to their initial letter in the rendered index
    for letter in string.ascii_uppercase:
        if letter in items_by_letter:
            for item_data in items_by_letter[letter]:
                                
                #build the HTML for the individual index entry
                rendered_html = html_renderer(item_data)
                
                #store the entry's initial letter as a data attribute so
                #that frontend filtering can show or hide entries by letter
                first_letter = letter
                
                html.append(
                    f"<li class='letter-entry' data-letter='{first_letter}'>{rendered_html}</li>"
                )
    
    html.append("</ul>")

    return "\n".join(html)


def render_page(title, body_html):
    return [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        "  <meta charset='UTF-8'>",
        "  <meta name='viewport' content='width=device-width, initial-scale=1'>",
        f"  <title>{esc(title)}</title>",

        #load the index-specific stylesheet and Bootstrap
        "  <link rel='stylesheet' href='../static/css/index.css'>",
        "   <link href='https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css' rel='stylesheet' integrity='sha384-rbsA2VBKQhggwzxH7pPCaAqO46MgnOM80zW1RWuH61DGLwZJEdK2Kadq2F9CUG65' crossorigin='anonymous'>",
        "</head>",
        "<body>",

        #keep the index controls fixed at the top of the page while
        #the user scrolls through the entity entries
        "<div class='sticky-top bg-white border-bottom'>",
        "<div class='index-header d-flex flex-column flex-md-row justify-content-between align-items-md-center'>",
        f"  <h1>{esc(title)}</h1>",

        #render the search controls and alphabetical navigation used
        #to filter and navigate the index entries
        *render_search(),
        "</div>",
        *render_alphabet_nav(),

        #provide a container for the frontend to display the current
        #number of visible results after filtering
        "  <div id='entry-count' class='px-2 py-2 results-num'></div>",
        "</div>",

        #insert the rendered index entries into the main page content
        "  <main>",
        body_html,
        "  </main>",

        #load Bootstrap's JavaScript bundle followed by the custom
        #index JavaScript responsible for search and filtering behaviour
        "  <script src='https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js' integrity='sha384-kenU1KFdBIe4zVF0s0G1M5b4hcpxyD9F7jL+jjXkk+Q2h455rYXK/7HAuoJl+0I4' crossorigin='anonymous'></script>",
        "  <script src='../static/js/index.js'></script>",
        "</body>",
        "</html>",
    ]

