/*
Functions for names
*/

/**
 * Handles the addition of a new name. \
 * Send a POST request to the server to add a new name. If the request is successful, add the new name to the names list.
 *
 * @example
 * The body of the request is a JSON object with the following structure:
 * ```
 * {
 *  "artist_name": "New name",
 *  "original_artist_name": "Original name"
 * }
 * ```
 * \
 * The new name is fetched from the `newNameInput` input field. \
 * The original name is fetched from the `newOriginalNameInput` input field. \
 */
const addName = async () => {
  try {
    // Get the new name and original name values from the input fields
    const newNameInput = document.getElementById("newNameInput");
    const newName = newNameInput.value;

    const newOriginalNameInput = document.getElementById(
      "newOriginalNameInput"
    );
    const newOriginalName = newOriginalNameInput.value;

    // Validate that the new name is not empty
    if (newName.trim() === "") {
      populateModal("ERROR", "Name cannot be empty");
      return;
    }

    // Send a POST request to the server to add a new name
    const response = await fetch(`names/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        artist_name: newName,
        original_artist_name: newOriginalName,
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

    // If successful, add the new name to the names list
    const data = await response.json();
    newNameInput.value = "";
    newOriginalNameInput.value = "";
    insertItemName(data.id, data.artist_name, data.original_artist_name);
  } catch (error) {
    // Catch any errors that occur during the process and display an error message
    populateModal("ERROR", error.message);
  }
};

/**
 * Handles the editing of a new name. \
 * Send a PUT request to the server to update the name. If the request is successful, no additional handling is needed.
 * @param {number} nameId - The unique identifier of the name to be removed (link_artist_name.id).
 * @example
 * The body of the request is a JSON object with the following structure:
 * ```
 * {
 *  "artist_name": "New name",
 *  "original_artist_name": "Original name"
 * }
 * ```
 * \
 * The new name is fetched from the `nameInput_${nameId}` input field. \
 * The original name is fetched from the `originalNameInput_${nameId}` input field. \
 */
const editArtistName = async (nameId) => {
  try {
    // Get the new name and original name values from the input fields
    const newNameInput = document.getElementById(`name-${nameId}`);
    const newName = newNameInput.value;

    const newOriginalNameInput = document.getElementById(
      `originalName-${nameId}`
    );
    const newOriginalName = newOriginalNameInput.value;

    // Validate that the new name is not empty
    if (newName.trim() === "") {
      populateModal("ERROR", "Name cannot be empty");
      return;
    }

    // Send a PUT request to the server to update the name
    const response = await fetch(`names/${nameId}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        artist_name: newName,
        original_artist_name: newOriginalName,
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

    // If successful, no additional handling is needed
  } catch (error) {
    // Catch any errors that occur during the process and display an error message
    populateModal("ERROR", error.message);
  }
};

/**
 * Handles the removal of a name.
 * Remove the name from the database through a DELETE request to the server. If the request is successful, remove the corresponding element from the DOM.
 * @param {number} nameId - The unique identifier of the name to be removed (link_artist_name.id).
 */
const removeArtistName = async (nameId) => {
  try {
    // Send a DELETE request to the server
    const response = await fetch(`names/${nameId}`, {
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

    // If successful, remove the corresponding element from the DOM
    const item = document.getElementById(`item-${nameId}`);
    if (item) {
      item.parentNode.removeChild(item);
    } else {
      throw new Error("Element not found in the DOM.");
    }
  } catch (error) {
    // Catch any errors that occur during the process and display an error message
    populateModal("ERROR", error.message);
  }
};

/**
 * Inserts a new name item into the 'nameList' list from artist update page.
 * @param {number} nameId - The unique identifier for the name (link_artist_name.id).
 * @param {string} newName - The name to be displayed and edited (link_artist_name.artist_name).
 * @param {string} newOriginalName - The original name associated with the displayed name (link_artist_name.original_artist_name).
 */
const insertItemName = (nameId, newName, newOriginalName) => {
  // Get the reference to the name list container
  const nameList = document.getElementById("nameList");

  // Create a new list item element
  const newItem = document.createElement("li");
  newItem.id = `item_${nameId}`;
  newItem.className = "sortable-item";
  newItem.dataset.id = nameId;

  // Set the inner HTML content for the new item
  newItem.innerHTML = `
    <div class="columns">
        <div class="column is-5">
            <input type="text"
                   class="input is-small"
                   id="nameInput_${nameId}"
                   value="${newName}">
        </div>
        <div class="column is-5">
            <input type="text"
                   class="input is-small"
                   id="originalNameInput_${nameId}"
                   value="${newOriginalName}">
        </div>
        <div class="column is-2">
            <div class="buttons">
                <button class="button is-small is-success" onclick="editArtistName(${nameId})">Save</button>
                <button class="button is-small is-danger" onclick="removeArtistName(${nameId})">Delete</button>
            </div>
        </div>
    </div>
  `;

  // Append the new item to the name list container
  nameList.appendChild(newItem);
};

/**
 * Creates a sortable name list using Sortable.js. \
 * The list is made sortable by dragging and dropping the items. \
 * The order of the items is updated in the database through a PUT request to the server. If the request is successful, no additional handling is needed.
 * @param {string} listName - The ID of the list element to be made sortable.
 * @example
 * The body of the request is a JSON object with the following structure:
 * ```
 * [
 *    {"id": 1, "order": 1},
 *    {"id": 2, "order": 2}
 * ]
 * ```
 *
 * The `id` is the unique identifier for the name (link_artist_name.id). \
 * The `order` is the new order of the name in the list. (link_artist_name.order)
 */
const createSortableNameList = (listName) => {
  // Get the reference to the name list container
  const nameList = document.getElementById(listName);

  // Initialize Sortable.js for the specified list
  new Sortable(nameList, {
    onEnd: async (event) => {
      // Get the updated order of names after reordering
      const updatedOrder = Array.from(nameList.children).map(
        (listItem, index) => {
          const nameId = listItem.dataset.id;
          return { id: nameId, order: index + 1 };
        }
      );

      // Send a PUT request to the server to update the order of the names
      const response = await fetch(`names/${nameId}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ order: updatedOrder }),
      });

      // Check if the request was successful
      if (!response.ok) {
        // If not successful, handle the error
        const errorMessage = await response.text();
        throw new Error(
          `${response.status} ${response.statusText}. ${errorMessage}`
        );
      }

      // If successful, no additional handling is needed
    },
  });
};

/*
Functions for Line Ups
*/

/**
 * Adds a new lineup for a given artist.
 * @param {number} idArtist - The unique identifier of the artist.
 */
const addLineUp = async (idArtist) => {
  try {
    // Send a POST request to create a new lineup for the artist
    const response = await fetch(`/artists/${idArtist}/line_ups/`, {
      method: "POST",
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

    // Parse the response JSON
    const data = await response.json();

    // Extract feedback message from the response data
    const feedbackMessage =
      data && data.feedback ? data.feedback : data.error || "";

    // Display success message and reload the page
    if (!feedbackMessage) {
      window.location.reload();
    }

    populateModal("SUCCESS", feedbackMessage);

    // TODO: If successful, add the new lineup to the lineup list
    // window.location.reload();
  } catch (error) {
    // Catch any errors that occur during the process and display an error message
    populateModal("ERROR", error.message);
  }
};

/**
 * Removes a lineup with the given identifier.
 * @param {number} idLineUp - The unique identifier of the lineup.
 */
const removeLineUp = async (idLineUp) => {
  try {
    // Send a DELETE request to remove the lineup
    const response = await fetch(`/line_ups/${idLineUp}`, {
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

    // Parse the response JSON
    const data = await response.json();

    // Extract feedback message from the response data
    const feedbackMessage =
      data && data.feedback ? data.feedback : data.error || "";

    // Display success message and reload the page
    if (!feedbackMessage) {
      window.location.reload();
    }

    populateModal("SUCCESS", feedbackMessage);

    // TODO: If successful, remove the lineup from the lineup list
    // window.location.reload();
  } catch (error) {
    // Catch any errors that occur during the process and display an error message
    populateModal("ERROR", error.message);
  }
};

/*
Functions for Line Ups members
*/

/**
 * Adds a new member to a lineup.
 * @param {number} idLineUp - The unique identifier of the lineup.
 * @example
 * The body of the request is a JSON object with the following structure:
 * ```
 * {
 * "id_member": 1,
 * "id_member_line_up": 1,
 * "id_role_type": 1
 * }
 * ```
 *
 * The `id_member` is the unique identifier for the name (link_artist_line_up.id_member). \
 * The `id_member_line_up` is the unique identifier for the lineup (link_artist_line_up.id_line_up). \
 * The `id_role_type` is the unique identifier for the role type (link_artist_line_up.id_role_type). \
 */
const addLineUpMember = async (idLineUp) => {
  try {
    // Get references to input elements
    const artistInput = document.getElementById(`hidden-artist-${idLineUp}`);
    const idMember = artistInput.value;
    const artistLineUpInput = document.getElementById(
      `add-line-up-${idLineUp}`
    );
    const idMemberLineUp = artistLineUpInput.value;
    const roleTypeInput = document.getElementById(`add-role-type-${idLineUp}`);
    const selectedRoleTypeOption =
      roleTypeInput.options[roleTypeInput.selectedIndex];
    const idRoleType = selectedRoleTypeOption.value;

    // Validate that the artist field is not empty
    if (idMember === "") {
      populateModal("ERROR", "Artist must be specified");
      return;
    }

    // Send a POST request to add a new member to the lineup
    const response = await fetch(`/line_ups/${idLineUp}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        id_member: idMember,
        id_member_line_up: idMemberLineUp,
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

    // If successful, add the new member to the member list
    const responseData = await response.json();

    // Get additional information for the new member
    const memberNameInput = document.getElementById(`add-artist-${idLineUp}`);
    const memberName = memberNameInput.value || "None";

    // Call a function to insert the new member into the list
    insertNewArtistItem(
      responseData.id,
      memberName,
      responseData.id_member,
      responseData.id_member_line_up || "None",
      selectedRoleTypeOption.text,
      "removeLineUpMember",
      `member-list-${idLineUp}`
    );
  } catch (error) {
    // Catch any errors that occur during the process and display an error message
    populateModal("ERROR", error.message);
  }
};

/**
 * Removes a member from the lineup's member list.
 * @param {number} idLinkArtistLineUp - The unique identifier of the link between artist and lineup.
 */
const removeLineUpMember = async (idLinkArtistLineUp) => {
  try {
    // Send a DELETE request to remove the member from the lineup
    const response = await fetch(`/line_ups/members/${idLinkArtistLineUp}`, {
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

    // Get the member list item based on the unique identifier
    const memberListItem = document.querySelector(
      `.artist-item[data-id="${idLinkArtistLineUp}"]`
    );

    // Remove the member list item from the DOM
    memberListItem.parentNode.removeChild(memberListItem);
  } catch (error) {
    // Catch any errors that occur during the process and display an error message
    populateModal("ERROR", error.message);
  }
};
