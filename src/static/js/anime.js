/**
 * Handles the editing of a new name. \
 * Send a PUT request to the server to update the name. If the request is successful, no additional handling is needed.
 * @param {number} nameId - The unique identifier of the name to be removed (link_anime_name.id).
 * @example
 * The body of the request is a JSON object with the following structure:
 * ```
 * {
 *  "original_anime_name": "Original name"
 * }
 * ```
 * \
 * The new name is fetched from the `nameInput_${nameId}` input field. \
 * The original name is fetched from the `originalNameInput_${nameId}` input field. \
 */
const editAnimeName = async (nameId) => {
  try {
    const newOriginalNameInput = document.getElementById(
      `original-name-${nameId}`
    );
    const newOriginalName = newOriginalNameInput.value;

    console.log(newOriginalName);

    // Send a PUT request to the server to update the name
    const response = await fetch(`names/${nameId}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        original_anime_name: newOriginalName,
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
