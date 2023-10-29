/**
 * Adds a new artist to the song.
 * @param {string} idElement - The identifier element used to construct element IDs.
 */
const addSongArtist = async (idElement) => {
  try {
    // Get references to input elements
    const artistInput = document.getElementById(`hidden-artist-${idElement}`);
    const idArtist = artistInput.value;
    const artistLineUpInput = document.getElementById(
      `add-line-up-${idElement}`
    );
    const idArtistLineUp = artistLineUpInput.value;
    const roleTypeInput = document.getElementById(`add-role-type-${idElement}`);
    const selectedRoleTypeOption =
      roleTypeInput.options[roleTypeInput.selectedIndex];
    const idRoleType = selectedRoleTypeOption.value;

    // Get the song ID from the URL
    const url = window.location.href;
    const songId = url.split("/")[4];

    // Validate that the artist field is not empty
    if (idArtist === "") {
      populateModal("ERROR", "Artist must be specified");
      return;
    }

    // Send a POST request to add the new artist to the song
    const response = await fetch(`/songs/artist/add/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        id_song: songId,
        id_artist: idArtist,
        id_artist_line_up: idArtistLineUp,
        id_role_type: idRoleType,
      }),
    });

    // Check if the request was successful
    if (!response.ok) {
      // If not successful, handle the error
      const errorMessage = await response.text();
      throw new Error(
        `${response.status} ${response.statusText}. ${errorMessage}`
      );
    }

    // Parse the response data
    const responseData = await response.json();

    // Log the response data for debugging purposes
    console.log(responseData);

    // If successful, add the new artist to the list
    // Get additional information for the new artist
    const artistNameInput = document.getElementById(`add-artist-${idElement}`);
    const artistName = artistNameInput.value;

    // Call a function to insert the new member into the list
    insertNewArtistItem(
      responseData.id,
      artistName,
      responseData.id_artist,
      responseData.id_artist_line_up || "None",
      selectedRoleTypeOption.text,
      "removeSongArtist",
      `song-artist-list-${idElement}`
    );
  } catch (error) {
    // Catch any errors that occur during the process and display an error message
    populateModal("ERROR", error.message);
  }
};

/**
 * Removes an artist from the song.
 * @param {string} idElement - The identifier element used to construct element IDs.
 */
const removeSongArtist = async (idElement) => {
  try {
    // Send a DELETE request to remove the artist from the song
    const response = await fetch(`/songs/artists/${idElement}`, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
      },
    });

    // Check if the request was successful
    if (!response.ok) {
      // If not successful, handle the error
      const errorMessage = await response.text();
      throw new Error(
        `${response.status} ${response.statusText}. ${errorMessage}`
      );
    }

    // Get the artist item based on the unique identifier
    const songArtistListItem = document.querySelector(
      `.artist-item[data-id="${idElement}"]`
    );

    // Remove the artist item from the DOM
    if (songArtistListItem) {
      songArtistListItem.parentNode.removeChild(songArtistListItem);
    } else {
      console.warn(`Artist item with id ${idElement} not found.`);
    }
  } catch (error) {
    // Catch any errors that occur during the process and display an error message
    populateModal("ERROR", error.message);
  }
};
