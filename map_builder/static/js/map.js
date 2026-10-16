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
    const searchCount = document.getElementById("film-search-count");

    if (!searchInput) {
        console.error("Search input not found.");
        return;
    }

    searchInput.addEventListener("input", function () {
        const query = searchInput.value.trim().toLowerCase();
        const data = window.screeningSearchData || [];

        // Find locations matching the search query.
        const matches = data.filter(item => {
            const searchableText = [
                item.Venue,
                ...(item.film_titles || []),
                ...(item.directors || []),
                item.location,
            ]
                .filter(Boolean)
                .join(" ")
                .toLowerCase();

            return searchableText.includes(query);
        });

        // Update the number of matching locations.
        if (searchCount) {
            searchCount.textContent = query
                ? `${matches.length} matching venues`
                : `${data.length} venues`;
        }

        // Create a set of matching venue names.
        const matchingVenues = new Set(
            matches.map(item =>
                String(item.Venue).trim().toLowerCase()
            )
        );

        // Highlight matching markers and fade the others.
        if (window.screeningMap && window.L) {
            window.screeningMap.eachLayer(function (layer) {
                if (
                    layer instanceof L.CircleMarker &&
                    layer.options.venueName
                ) {
                    const location = String(
                        layer.options.venueName
                    ).trim().toLowerCase();

                    const isMatch =
                        query === "" ||
                        matchingVenues.has(location);

                    layer.setStyle({
                        opacity: isMatch ? 1 : 0.15,
                        fillOpacity: isMatch ? 0.7 : 0.05
                    });
                }
            });
        }

        console.log("Matching venues:", matches);
        console.log("Map available:", !!window.screeningMap);
        console.log("Matching venues:", matches.length);

        if (window.screeningMap) {
            window.screeningMap.eachLayer(function (layer) {
                if (layer instanceof L.CircleMarker) {
                    console.log(
                        "Marker found:",
                        layer.options.venueName
            );
        }
    });
}
    });
});
