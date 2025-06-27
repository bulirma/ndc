var imageViewElem;

function onImageFileChange(e) {
    const file = e.target.files[0];
    if (file === undefined) { return; }

    const fileReader = new FileReader();
    fileReader.addEventListener('load', (e) => {
        const imgElem = document.createElement('img');
        imgElem.src = e.target.result;
        while (imageViewElem.firstChild) {
            imageViewElem.removeChild(imageViewElem.firstChild);
        }
        imageViewElem.appendChild(imgElem);
    });
    fileReader.readAsDataURL(file);
}

function onLoad() {
    imageViewElem = document.getElementById('image-preview');

    // file input element
    let sheetInputElem = document.getElementById('sheet-photography');
    sheetInputElem.addEventListener('change', onImageFileChange);

    if (sheetInputElem.files.length > 0) {
        const event = new Event('change', {
            target: sheetInputElem
        });
        sheetInputElem.dispatchEvent(event);
    }
}

window.addEventListener('load', onLoad);
