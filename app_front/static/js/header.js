

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