function scrollSlider(direction) {
    const track = document.getElementById('categoryTrack');
    track.scrollBy({
        left: direction * 300,
        behavior: 'smooth'
    });
}