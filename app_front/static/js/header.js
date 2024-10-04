

// Найти элемент по классу

// Добавить обработчик событий click
button = document.querySelector('.menu-button');

button.addEventListener('click', () => {
    const element = document.querySelector('.long-menu');

    if (element) {
        // Проверить текущее состояние display и переключить его
        if (element.style.display === 'flex') {
            element.style.cssText = '';
        } else {
            element.style.display = 'flex';
        }
    }
});

document.addEventListener('scroll', function() {
    const image = document.querySelector('.image-container img');
    const scrollPosition = window.scrollY;

    // Измените значение 0.5 для настройки скорости перемещения изображения
    const translateY = scrollPosition * 0.5;
    image.style.transform = `translate(-50%, calc(-50% + ${translateY}px))`;
});