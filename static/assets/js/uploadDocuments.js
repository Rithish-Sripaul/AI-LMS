let fileNameCard = document.getElementById("file-name-card");
let uploadedFile = document.getElementById("uploadedFile");

function upload() {
  console.log(uploadedFile);
  fileNameCard.innerHTML = `Uploaded File: <br> ${uploadedFile.value
    .split("\\")
    .pop()}`;
}

// Author and email input creation
let addAuthorBtn = document.getElementById("addAuthorBtn");
let authorCount = 2;
// Modal for spinner
let uploadForm = document.getElementById("uploadForm");
var ocrModal = new bootstrap.Modal(document.getElementById("exampleModal"), {
  keyboard: false,
});

uploadForm.addEventListener("submit", () => {
  ocrModal.toggle();
});

// Reset the form
function resetForm() {
  let subReportTypeContainer = document.getElementById(
    "subReportTypeContainer"
  );
  subReportTypeContainer.remove();
}

// Deleting Author Section
function deleteAuthorSection(btn) {
  let parent = btn.closest(".newAuthorSection");
  parent.remove();
  authorCount--;
}
