async function loadSearchData() {
    try {
        const response = await fetch("./search_data.json");

        if (!response.ok) {
            throw new Error(
                `Failed to load search_data.json: ${response.status} ${response.statusText}`
            );
        }

        const data = await response.json();

        console.log("Fetched URL:", response.url);
        console.log("Fetched data:", data);


        if (!Array.isArray(data)) {
            throw new Error("Search data should be a JSON array.");
        }

        console.log(`Loaded ${data.length} searchable venues.`);
        return data;

    } catch (error) {
        console.error("Could not load search data:", error);
        return [];
    }
}

loadSearchData().then(data => {
    // Make the data available to the existing search interface.
    window.screeningSearchData = data;

    console.log("Search data:", data);
    console.log(`Loaded ${data.length} searchable venues.`);
});

document.addEventListener("DOMContentLoaded", function () {
    const searchInput = document.getElementById("film-search-input");
    const searchType = document.getElementById("film-search-type");
    const suggestionsBox = document.getElementById("film-search-suggestions");
    const searchCount = document.getElementById("film-search-count");

    if (!searchInput || !searchType || !suggestionsBox) {
        console.error("Search controls not found.");
        return;
    }

    const fields = {
        location: item => [item.location],
        venue: item => [item.Venue],
        film: item => item.film_titles || [],
        director: item => item.directors || []
    };

    function normalizeText(value) {
        return String(value)
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .toLowerCase();
    }

    function getData() {
        return window.screeningSearchData || [];
    }

    function getMatches(query) {
        const field = fields[searchType.value];
        const normalizedQuery = normalizeText(query);

        return getData().filter(item => {
            const values = field(item).filter(Boolean);

            return !normalizedQuery || values.some(value =>
                normalizeText(value).includes(normalizedQuery)
            );
        });
    }

    function runSearch(value = searchInput.value) {
        const query = value.trim().toLowerCase();
        const matches = getMatches(query);

        if (searchCount) {
            searchCount.textContent = query
                ? `${matches.length} matching venues`
                : `${getData().length} venues`;
        }

        const matchingVenues = new Set(
            matches.map(item =>
                String(item.Venue).trim().toLowerCase()
            )
        );

        if (window.screeningMap && window.L) {
            window.screeningMap.eachLayer(function (layer) {
                if (!(layer instanceof L.CircleMarker)) return;

                const venue = String(layer.options.venueName || "")
                    .trim()
                    .toLowerCase();

                const isMatch = !query || matchingVenues.has(venue);

                layer.setStyle({
                    opacity: isMatch ? 1 : 0.15,
                    fillOpacity: isMatch ? 0.7 : 0.05
                });
            });
        }
    }

    function renderSuggestions(query) {
        suggestionsBox.replaceChildren();

        if (query.length < 2) {
            suggestionsBox.style.display = "none";
            return;
        }

        const field = fields[searchType.value];
        const seen = new Set();
        const suggestions = [];

        getData().forEach(item => {
            field(item).filter(Boolean).forEach(value => {
                const label = String(value).trim();
                const key = normalizeText(label);

                if (
                    normalizeText(label).includes(normalizeText(query)) &&
                    !seen.has(key)
                ) {
                    seen.add(key);
                    suggestions.push(label);
                }
            });
        });

        suggestionsBox.style.display = "block";

        if (suggestions.length === 0) {
            const empty = document.createElement("div");
            empty.textContent = "No matching suggestions";
            empty.className = "search-suggestion-empty";
            suggestionsBox.appendChild(empty);
            return;
        }

        suggestions.slice(0, 8).forEach(label => {
            const option = document.createElement("button");
            option.type = "button";
            option.className = "search-suggestion";
            option.textContent = label;

            option.addEventListener("click", function () {
                searchInput.value = label;
                suggestionsBox.style.display = "none";
                runSearch(label);
            });

            suggestionsBox.appendChild(option);
        });
    }

    searchInput.addEventListener("input", function () {
        renderSuggestions(searchInput.value.trim());
        runSearch();
    });

    searchType.addEventListener("change", function () {
        const placeholders = {
            location: "Search locations...",
            venue: "Search venues...",
            film: "Search films...",
            director: "Search directors..."
        };

        searchInput.placeholder = placeholders[searchType.value];
        suggestionsBox.style.display = "none";

        renderSuggestions(searchInput.value.trim());
        runSearch();
    });

    document.addEventListener("click", function (event) {
        if (
            !suggestionsBox.contains(event.target) &&
            event.target !== searchInput
        ) {
            suggestionsBox.style.display = "none";
        }
    });

    runSearch();
});

