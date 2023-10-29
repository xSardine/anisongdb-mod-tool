/*
Artist search autocompletion
*/

/**
 * Handles the selection of an artist from the autocomplete dropdown.
 * @param {object} artist - The selected artist object.
 * @param {string} idElement - The identifier element used to construct element IDs.
 */
function selectArtist(artist, idElement) {
  // Get references to relevant DOM elements
  const searchInput = document.getElementById("add-artist-" + idElement);
  const artistSearchInputDropdown = document.getElementById(
    "add-artist-dropdown-" + idElement
  );
  const idInput = document.getElementById("hidden-artist-" + idElement);

  // Set the search input value and the hidden artist ID input value
  searchInput.value = artist.names[0].artist_name;
  idInput.value = artist.id;

  // Hide the artist search input dropdown
  artistSearchInputDropdown.classList.remove("show");

  // Fetch lineup autocompletion for the selected artist
  fetchLineUpAutocompletion(artist.id);
}

/**
 * Fetches artist autocomplete data based on the given search term.
 * @param {string} searchTerm - The term to search for in artist names.
 */
async function fetchArtistAutocompletion(searchTerm) {
  try {
    const response = await fetch(
      `/autocomplete/artists?limit=100&search=${searchTerm}`
    );

    if (!response.ok) {
      throw new Error(`${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    autocompleteArtist = data; // Store fetched artist data
  } catch (error) {
    console.error("Error fetching artists:", error);
  }
}

/**
 * Fetches lineup autocomplete data based on the given artist ID.
 * @param {number} idArtist - The unique identifier of the artist.
 */
async function fetchLineUpAutocompletion(idArtist) {
  try {
    const response = await fetch(
      `/autocomplete/line_ups?id_artist=${idArtist}`
    );

    if (!response.ok) {
      throw new Error(`${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    autocompleteLineUp = data; // Store fetched lineup data
  } catch (error) {
    console.error("Error fetching lineups:", error);
  }
}

/**
 * Handles the artist search functionality.
 * @param {string} idElement - The identifier element used to construct element IDs.
 */
function handleArtistSearch(idElement) {
  // Get references to relevant DOM elements
  const artistSearchInput = document.getElementById("add-artist-" + idElement);
  const artistSearch = artistSearchInput.value.toLowerCase();
  const artistSearchInputDropdown = document.getElementById(
    "add-artist-dropdown-" + idElement
  );
  const idInput = document.getElementById("hidden-artist-" + idElement);

  // Clear state and return early if the search term is empty
  if (artistSearch === "") {
    idInput.value = null;
    artistSearchInputDropdown.classList.remove("show");
    autocompleteArtist = [];
    return;
  }

  // Fetch artist autocomplete data based on the search term
  fetchArtistAutocompletion(artistSearch);

  // Filter matching artists based on the autocomplete data
  const matchingArtist = autocompleteArtist.filter(
    (artist) =>
      artist.names.some((artist_name) =>
        artist_name.artist_name?.toLowerCase().includes(artistSearch)
      ) ||
      artist.names.some((artist_name) =>
        artist_name.original_artist_name?.toLowerCase().includes(artistSearch)
      )
  );

  // Clear existing options in the dropdown
  artistSearchInputDropdown.innerHTML = "";

  // Populate the dropdown with matching artist options
  matchingArtist.forEach((artist) => {
    let option = document.createElement("div");
    option.textContent = artist.names[0].artist_name;
    option.classList.add("autocomplete-option");
    option.addEventListener("click", function () {
      selectArtist(artist, idElement);
    });
    artistSearchInputDropdown.appendChild(option);
  });

  // Show or hide the dropdown based on the number of matching artists
  artistSearchInputDropdown.classList.toggle("show", matchingArtist.length > 0);
}

/**
 * Hides the artist dropdown after a delay.
 * @param {string} idElement - The identifier element used to construct element IDs.
 */
function hideArtistDropdown(idElement) {
  const inputDropdown = document.getElementById(
    "add-artist-dropdown-" + idElement
  );
  blurTimeout = setTimeout(() => {
    inputDropdown.classList.remove("show");
  }, 200); // Adjust the delay time as needed
}

/**
 * Handles the selection of a lineup from the autocomplete dropdown.
 * @param {object} line_up - The selected lineup object.
 * @param {string} idElement - The identifier element used to construct element IDs.
 */
function selectLineUp(line_up, idElement) {
  const lineUpInput = document.getElementById("add-line-up-" + idElement);
  const lineUpInputDropdown = document.getElementById(
    "add-line-up-dropdown-" + idElement
  );
  lineUpInput.value = line_up.id;
  lineUpInputDropdown.classList.remove("show");
}

/**
 * Handles the lineup search functionality.
 * @param {string} idElement - The identifier element used to construct element IDs.
 */
function handleLineUp(idElement) {
  console.log(idElement);

  // Get references to relevant DOM elements
  const searchInput = document.getElementById("add-artist-" + idElement);
  const lineUpInput = document.getElementById("add-line-up-" + idElement);
  const lineUpInputDropdown = document.getElementById(
    "add-line-up-dropdown-" + idElement
  );

  // Clear the lineup input value if the artist search input is empty
  if (searchInput.value == "") {
    lineUpInput.value = "";
    return;
  }

  // Fetch lineup autocomplete data based on the search term
  fetchLineUpAutocompletion(lineUpInput.value);

  console.log(autocompleteLineUp);

  // Clear the lineup input value if no autocomplete data is available
  if (autocompleteLineUp.length == 0) {
    lineUpInput.value = "";
    return;
  }

  // Remove existing options in the dropdown
  lineUpInputDropdown.innerHTML = "";

  // Populate the dropdown with matching lineup options
  autocompleteLineUp.forEach((line_up) => {
    let option = document.createElement("div");

    // Create a string with lineup ID and member names
    const members = line_up.members
      ?.map((member) => member.names[0].artist_name)
      .join(", ");

    option.textContent = line_up.id + " (" + members + ")";
    option.classList.add("autocomplete-option");
    option.addEventListener("click", function () {
      selectLineUp(line_up, idElement);
    });
    lineUpInputDropdown.appendChild(option);
  });

  // Show the lineup dropdown
  lineUpInputDropdown.classList.add("show");
}

/**
 * Hides the lineup dropdown after a delay.
 * @param {string} idElement - The identifier element used to construct element IDs.
 */
function hideLineUp(idElement) {
  // Get reference to the lineup dropdown
  const lineUpInputDropdown = document.getElementById(
    "add-line-up-dropdown-" + idElement
  );

  // Set a delay using setTimeout to hide the dropdown
  blurTimeout = setTimeout(() => {
    lineUpInputDropdown.classList.remove("show");
  }, 200); // Adjust the delay time as needed
}

/**
 * Inserts a new artist item into the specified artist list.
 * @param {number} idLink - The unique identifier for the artist link.
 * @param {string} artistName - The name of the artist.
 * @param {number} idArtist - The unique identifier for the artist.
 * @param {number} idLineUp - The unique identifier for the lineup.
 * @param {string} roleType - The role type of the artist.
 * @param {function} removeFunction - The function to call when removing the artist.
 * @param {string} artistListId - The ID of the artist list container.
 */
const insertNewArtistItem = (
  idLink,
  artistName,
  idArtist,
  idLineUp,
  roleType,
  removeFunction,
  artistListId
) => {
  // Create a new list item element for the new artist
  const newArtistItem = document.createElement("li");
  newArtistItem.classList.add("artist-item");
  newArtistItem.setAttribute("data-id", idLink);

  // Set the inner HTML content for the new artist item
  newArtistItem.innerHTML = `
    <div class="columns">
      <div class="column is-3">
        <input class="input is-small" type="text" id="name-${idLink}-${idArtist}" value="${artistName}" disabled>
      </div>
      <div class="column is-3">
        <input class="input is-small" type="text" id="line-up-${idLink}-${idArtist}" value="${idLineUp}" title="TODO" disabled>
      </div>
      <div class="column is-2">
        <input class="input is-small" type="text" id="role-type-${idLink}-${idArtist}" value="${roleType}" disabled>
      </div>
      <div class="column">
        <button class="button is-small is-danger" onclick="${removeFunction}(${idLink})">Remove</button>
        <a class="button is-small is-link" href="/artists/${idArtist}/" target="_blank">See</a>
      </div>
    </div>
  `;

  // Append the new artist item to the artist list
  const artistList = document.getElementById(artistListId);
  artistList.appendChild(newArtistItem);
};
