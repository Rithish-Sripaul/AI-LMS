// Deleting Author Section
function deleteLesson(btn) {
  let parent = btn.closest(".newAuthorSection");
  parent.remove();
  authorCount--;
}
