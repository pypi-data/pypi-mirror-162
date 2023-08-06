/**
* Copies the inner text in an element to the clipboard.
* @param   {String} elem_id   The ID of the element to search for innerText.
*/
function copy_to_clipboard(elem_id) {
  var elem = document.getElementById(elem_id);
  navigator.clipboard.writeText(elem.innerText);
}
