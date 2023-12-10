function Hide(HideID)
{
  HideID.style.display = "none";
}

window.addEventListener('load', (event) => {

document.getElementById('file-in').addEventListener('change', function(event) {

    let fileNameItem = document.getElementsByClassName('file-list')[0];
    fileNameItem.classList.remove('hidden');
    let fileNameLabel = document.getElementById('file-name-span');
    fileNameLabel.textContent = event.target.files[0].name;
});

});

