// ============================================================
// Index count
// ============================================================

// Count the total number of index entries and how many are
// currently visible within their letter group.
const countIndexEntries = () => {
  const entries = document.querySelectorAll('.index-entry');

  let count = 0;
  let countTotal = 0;

  entries.forEach(entry => {
    // Count every index entry towards the total.
    countTotal++;

    // Find the letter group containing this entry.
    const letterEntry = entry.closest('.letter-entry');
    if (!letterEntry) return;

    // Check the visibility of both the letter group and
    // the individual index entry.
    const letterStyle = window.getComputedStyle(letterEntry);
    const entryStyle = window.getComputedStyle(entry);

    const letterVisible = letterStyle.display !== "none";
    const entryVisible = entryStyle.display !== "none";

    // Only count entries that are visible at both levels.
    if (letterVisible && entryVisible) {
      count++;
    }
  });

  // Return the visible and total counts for the UI update.
  return { count, countTotal };
};


// Update the entry-count element with the current visible
// and total number of index entries.
const updateIndexCount = () => {
  const countEl = document.getElementById('entry-count');
  
  // Do nothing if this page does not contain an entry-count element.
  if (!countEl) return;

  const { count, countTotal } = countIndexEntries();

  // Display the visible number alongside the total number of entries.
  countEl.innerHTML = `<strong>${count}</strong> of <strong>${countTotal}</strong> entries`;
};


// ============================================================
// Page initialisation
// ============================================================

document.addEventListener('DOMContentLoaded', () => {
  
  
  // ----------------------------------------------------------
  // Find index elements
  // ----------------------------------------------------------

  // Find the elements used by the alphabet filter and index search.
  const buttons = document.querySelectorAll('.alphabet button');
  const entries = document.querySelectorAll('.letter-entry');
  const entriesIndex = document.querySelectorAll('.index-entry');
  const searchInput = document.getElementById("index-search");
  const groups = document.querySelectorAll('.letter-group');

  // Store the currently selected alphabet filter.
  // Start with "all" so no letter filter is applied.
  let activeLetter = "all";

  
  // ----------------------------------------------------------
  // Reset index
  // ----------------------------------------------------------

  // Reset the index to its default unfiltered state.
  const resetIndex = () => {
    
    // Reset the active alphabet filter.
    activeLetter = "all";

    // Clear the search input.
    if (searchInput) searchInput.value = "";

    // Show all letter groups and reset their open state.
    entries.forEach(entry => {
      entry.style.display = 'block';
      entry.classList.remove('open');
    });

    // Show all index entries and reset their open state.
    entriesIndex.forEach(entry => {
      entry.style.display = 'block';
      entry.classList.remove('open');
    });

    // Remove the active state from alphabet buttons.
    buttons.forEach(btn => btn.classList.remove('active-letter'));

    // Remove the active state from letter groups.
    groups.forEach(group => group.classList.remove('active'));

    // Update the visible/total entry count.
    updateIndexCount();

  };

  // Initialise the index in its default state.
  resetIndex();
  

  // ----------------------------------------------------------
  // Alphabet filter
  // ----------------------------------------------------------

  // Handle selection of an alphabet filter button.
  const handleLetterClick = (button) => {
    // Store the selected letter as the active filter.
    const letter = button.dataset.letter;
    activeLetter = letter;

    // Clear the search because the alphabet filter now controls the results.
    if (searchInput) {
      searchInput.value = "";
    }

    // Remove the active state from all alphabet buttons.
    buttons.forEach(btn => btn.classList.remove('active-letter', 'active-all'));

    // Reset the index completely when "All" is selected.
    if (letter === 'all') {
      button.classList.add('active-all');
      resetIndex();
      return;
    } 
        
    // Mark the selected letter as active.
    button.classList.add('active-letter');

    // Show only the letter group matching the selected letter.
    entries.forEach(entry => {
      const matchesLetter =
        entry.dataset.letter &&
        entry.dataset.letter.toUpperCase() === letter.toUpperCase();

      entry.style.display = matchesLetter ? 'block' : 'none';
    });

    // Show all index entries within the selected letter group
    // and close any entries that were previously open.
    entriesIndex.forEach(entry => {
      entry.style.display = 'block';
      entry.classList.remove('open');
    });

    // Update the visible/total entry count.
    updateIndexCount();
  };

  // Apply the letter filter when an alphabet button is clicked.
  buttons.forEach(button => {
    button.addEventListener('click', () => handleLetterClick(button));
  });


  // ----------------------------------------------------------
  // URL hash handling
  // ----------------------------------------------------------

  // Open and focus an index entry when its ID is supplied in the URL hash.
  function focusHashTarget() {
    const hash = window.location.hash;
    if (!hash) return;

    // Find the element referenced by the hash.
    const target = document.querySelector(hash);
    if (!target) return;

    // Only index entries and letter entries can be opened this way.
    const isEntry =
      target.classList.contains('index-entry') ||
      target.classList.contains('letter-entry');

    if (!isEntry) return;

    // Reset the index before displaying the hash target.
    resetIndex();

    // Make the target visible and open it.
    target.style.display = 'block';
    target.classList.add('open');

    // Mark the target's letter group as active.
    const section = target.closest('.letter-group');      
    if (section) {
      groups.forEach(group => group.classList.remove('active'));
      section.classList.add('active');
    }

    // Wait briefly for the target to be displayed before scrolling to it.
    setTimeout(() => {
      
      // Leave space for the fixed navigation bar at the top of the page.
      const navbarOffset = 140;

      // Calculate the target's position in the document and subtract
      // the navigation offset so the target is not hidden underneath it.
      const y =
        target.getBoundingClientRect().top +
        window.scrollY -
        navbarOffset;

      // Scroll smoothly to the target position.
      window.scrollTo({
        top: y,
        behavior: 'smooth'
      });

      // Temporarily highlight the target so it is easy to identify.
      target.classList.add('hash-highlight');        
      setTimeout(() => {
        target.classList.remove('hash-highlight');
      }, 2500);

      // Remove the hash from the URL after navigating to the target.
      history.replaceState(
        null,
        null,
        window.location.pathname + window.location.search
      );
    }, 50);
  }

  // Handle an initial hash and any subsequent hash changes.
  focusHashTarget();
  window.addEventListener('hashchange', focusHashTarget);


  // ----------------------------------------------------------
  // Index search
  // ---------------------------------------------------------- 

  // Stop if this page does not contain the index search.
  if (!searchInput) return;

  // Normalise text so searches treat accented and unaccented characters as equivalent.
  const normalizeText = (text) =>
    text.normalize("NFD").replace(/[\u0300-\u036f]/g, "");

  
  // Filter the index according to the search text and active letter.
  const performSearch = () => {
    const query = normalizeText(searchInput.value.trim());
    
    // Create a word-boundary search pattern when a query exists.
    // Leave the pattern null when the search box is empty.
    const regex = query ? new RegExp(`\\b${query}`, "i") : null;

    // Check each letter group against the active letter filter
    // and the search query.
    entries.forEach(letterEntry => {
      const matchesLetter =
        activeLetter === "all" ||
        letterEntry.dataset.letter.toUpperCase() === activeLetter.toUpperCase();

      // Keep track of how many entries in this group match the search.
      let visibleCount = 0;

      // Filter the individual entries within the letter group.
      letterEntry.querySelectorAll(".index-entry").forEach(entry => {
        const title = entry.querySelector(".entry-title");
        
        // Skip entries that do not contain a searchable title.
        if (!title) return;

        const text = normalizeText(title.textContent);
        const matchesSearch = !regex || regex.test(text);

        // An entry is visible only when it matches both filters.
        const visible = matchesLetter && matchesSearch;

        // Show or hide the individual entry according to the active
        // letter filter and search query.
        entry.style.display = visible ? "block" : "none";
        
        // Increment the count of visible entries in this group.
        if (visible) visibleCount++;
      });

      // Show the letter group when it contains at least one visible entry.
      // Hide it when none of its entries match.
      letterEntry.style.display = visibleCount ? "block" : "none";
    });

    // Update the visible/total entry count after filtering.
    updateIndexCount();
  };

  // Run the search whenever the user types or changes the search input.
  searchInput.addEventListener("input", performSearch);

  
  // ----------------------------------------------------------
  // Search clear button
  // ----------------------------------------------------------
  
  // Find the button used to clear the search field.
  const clearButton = document.getElementById("search-clear");
  
  // Add the clear behaviour when the button exists.
  if (clearButton) {
    clearButton.addEventListener("click", () => {
      // Clear the search field and trigger the normal search filtering.
      searchInput.value = "";
      searchInput.dispatchEvent(new Event("input"));
      
      // Return focus to the search field.
      searchInput.focus();

      // Reset the index to its default unfiltered state.
      resetIndex();

    });
  }
});


// ============================================================
// Entry click handlers
// ============================================================

// Handle clicks on item and entry headers using event delegation.
// This allows the handler to work for dynamically generated entries.
document.addEventListener('click', function (e) {
  
  // Check whether the click occurred on an item header.
  const itemHeader = e.target.closest(".item-header");
  
  // Toggle the item's open state when an item header is clicked.
  if (itemHeader) {
    itemHeader.parentElement.classList.toggle("open");
    return;
  }

  // Check whether the click occurred on an entry header.
  const entryHeader = e.target.closest(".entry-header");
  
  // Ignore clicks that are not on an entry header.
  if (!entryHeader) return;

  // Find the entry containing the clicked header.  
  const item = entryHeader.parentElement;
  
  // Find the metadata/details panel belonging to the entry.
  const details = item.querySelector(".item-details");
  
  // Stop if the entry does not contain a details panel.
  if (!details) return;

  // Check whether the details panel contains any metadata.
  if (details.children.length === 0) {
    
    // Only create the temporary message if one is not
    // already being displayed.
    if (!details.querySelector(".temp-no-metadata")) {
      
      // Create a temporary message indicating that no metadata exists.
      const msg = document.createElement("div");
      msg.className = "temp-no-metadata";
      msg.textContent = "No metadata";
      details.appendChild(msg);
      
      // Open the entry so the message is visible to the user.
      item.classList.add("open");

      // Remove the message and close the entry after two seconds.
      setTimeout(() => {
        msg.remove();
        item.classList.remove("open");
      }, 2000);
    }
    
    // Stop here because there is no metadata to toggle normally.
    return;
  }

  // Toggle the entry open or closed when metadata exists.
  item.classList.toggle("open");
});


