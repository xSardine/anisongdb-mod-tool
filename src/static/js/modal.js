/**
 * Populates the feedback modal with the provided title and body content.
 * @param {string} modalTitleContent - The HTLML content for the modal title.
 * @param {string} modalBodyContent - The HTML content for the modal body.
 */
const populateModal = async (modalTitleContent, modalBodyContent) => {
  // Get a reference to the feedback modal
  const feedbackModal = document.getElementById("feedbackModal");

  // Check if the modal element exists
  if (!feedbackModal) {
    console.error("Modal not found");
    return;
  }

  // Get references to the modal title and body elements
  const modalTitle = feedbackModal.querySelector(".modal-card-title");
  const modalBody = feedbackModal.querySelector(".modal-card-body");

  // Check if the modal elements are properly configured
  if (!modalBody || !modalTitle) {
    console.error("Modal is not properly configured");
    return;
  }

  // Set the content of the modal title and body
  modalTitle.innerHTML = modalTitleContent;
  modalBody.innerHTML = modalBodyContent;

  // Activate the modal
  feedbackModal.classList.add("is-active");
};

/**
 * Closes the modal and reloads the window.
 */
const closeModal = () => {
  // Reload the window to close the modal
  window.location.reload();
};
