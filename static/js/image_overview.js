var carouselItemElems;
var recordRowElems;
var selectedItemIndex = 0;

function setHighlightedItem(index) {
    recordRowElems[selectedItemIndex].classList.toggle('table-primary');
    selectedItemIndex = index;
    recordRowElems[selectedItemIndex].classList.toggle('table-primary');
}

function setActiveItem(index) {
    carouselItemElems[selectedItemIndex].classList.toggle('active');
    setHighlightedItem(index)
    carouselItemElems[selectedItemIndex].classList.toggle('active');
}

function onLoad() {
    const carousel = document.getElementById('sheet-overview-carousel');
    carouselItemElems = document.querySelectorAll('#sheet-overview-carousel .carousel-item');
    recordRowElems = document.querySelectorAll('#overview-table tbody tr');
    if (carouselItemElems.length > 0) {
        carouselItemElems[selectedItemIndex].classList.toggle('active');
        recordRowElems[selectedItemIndex].classList.toggle('table-primary');
    }
    for (let i = 0; i < recordRowElems.length; ++i) {
        recordRowElems[i].addEventListener('click', () => {
            setActiveItem(i);
        });
    }
    carousel.addEventListener('slide.bs.carousel', e => {
        setHighlightedItem(e.to);
    });
}

window.addEventListener('load', onLoad);
