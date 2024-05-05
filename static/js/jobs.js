// Ждем, пока весь HTML-документ загрузится
document.addEventListener('DOMContentLoaded', function () {
    // Получаем элементы формы поиска, контейнера результатов и пагинации
    const searchForm = document.querySelector('form');
    const resultsContainer = document.querySelector('#results-container');
    const paginationContainer = document.querySelector('.pagination');

    // Функция для выполнения AJAX-запроса и обновления результатов
    function fetchResults(url) {
        fetch(url, {
            // Устанавливаем заголовок, чтобы запрос определялся как AJAX
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json()) // Обрабатываем JSON-ответ
        .then(data => {
            // Обновляем контейнер результатов с новыми данными
            resultsContainer.innerHTML = data.jobs.map(job => `
                <li class="list-group-item d-flex justify-content-between align-items-center p-4 mb-3 shadow-lg rounded border-0">
                    <div>
                        <h4 class="fw-bold text-primary">${job.title}</h4>
                        <p class="mb-0 text-muted">${job.description}</p>
                    </div>
                    <a href="/jobs/public/${job.id}/" class="btn btn-info view-details">View Details</a>
                </li>
            `).join('');

            // Обновляем пагинацию с новыми данными
            paginationContainer.innerHTML = data.pagination;

            // Добавляем обработчик события клика для кнопок просмотра деталей
            document.querySelectorAll('.view-details').forEach(link => {
                link.addEventListener('click', function (event) {
                    event.preventDefault(); // Предотвращаем стандартное поведение
                    window.location.href = this.href; // Перенаправляем на URL детали
                });
            });
        });
    }

    // Обработчик события отправки формы поиска
    searchForm.addEventListener('submit', function (event) {
        event.preventDefault(); // Предотвращаем стандартное поведение отправки формы
        const query = searchForm.querySelector('input[name="q"]').value; // Получаем поисковой запрос
        const url = `/jobs/public/jobs/?q=${encodeURIComponent(query)}`; // Создаем URL для поиска
        fetchResults(url); // Получаем результаты с помощью AJAX
    });

    // Обработчик события клика на ссылки пагинации
    document.addEventListener('click', function (event) {
        if (event.target.classList.contains('pagination-link')) {
            event.preventDefault(); // Предотвращаем стандартное поведение клика
            const pageUrl = event.target.href; // Получаем URL страницы
            const query = searchForm.querySelector('input[name="q"]').value; // Получаем поисковой запрос
            // Формируем итоговый URL с поисковым запросом и номером страницы
            const finalUrl = pageUrl.includes('?') ? `${pageUrl}&q=${encodeURIComponent(query)}` : `${pageUrl}?q=${encodeURIComponent(query)}`;
            fetchResults(finalUrl); // Получаем результаты с помощью AJAX
        }
    });
});


document.addEventListener('DOMContentLoaded', function () {
    // Ensure the form has the id "opinionForm"
    const opinionForm = document.querySelector('#opinionForm');

    // Ensure the form exists before adding the event listener
    if (opinionForm) {
        // Handle AJAX form submission
        opinionForm.addEventListener('submit', function (event) {
            event.preventDefault(); // Prevent default form submission

            const formData = new FormData(opinionForm);

            fetch(opinionForm.action, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formData
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json(); // Expecting JSON response
            })
            .then(data => {
                // Handle successful submission
                if (data.success) {
                    if (data.redirect_url) {
                        // Redirect to the provided URL if present
                        window.location.href = data.redirect_url;
                    } else {
                        alert('Opinion submitted successfully!');
                        opinionForm.reset(); // Optionally reset the form
                    }
                } else {
                    // Display error messages from the server response
                    const errors = JSON.parse(data.errors);
                    for (const field in errors) {
                        const errorMessages = errors[field].map(error => error.message).join(', ');
                        alert(`${field}: ${errorMessages}`); // or display errors on the page
                    }
                }
            })
            .catch(error => {
                // Handle error during submission
                alert('An error occurred while submitting the opinion.');
                console.error('Error:', error);
            });
        });
    }
});


