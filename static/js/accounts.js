// Oczekiwanie na pełne załadowanie DOM
document.addEventListener('DOMContentLoaded', function () {

    // Funkcja do pobierania wyników za pomocą żądania AJAX
    function fetchResults(url, type) {
        fetch(url, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
            .then(response => response.json()) // Konwersja odpowiedzi na JSON
            .then(data => {
                // W zależności od typu, aktualizujemy odpowiedni interfejs użytkownika
                if (type === 'recruiters') {
                    updateRecruitersUI(data);
                } else if (type === 'clients') {
                    updateClientsUI(data);
                }
            });
    }

    // Funkcja do aktualizacji interfejsu użytkownika dla rekruterów
    function updateRecruitersUI(data) {
        const container = document.querySelector('#recruiters-container');
        // Generowanie kodu HTML dla listy rekruterów
        container.innerHTML = JSON.parse(data.recruiters).map(item => `
            <li class="list-group-item d-flex align-items-center p-4 mb-4 shadow-lg rounded border-0">
                <img src="${item.fields.photo || '/static/images/recruiter.png'}" class="rounded-circle me-4 border border-primary" style="width: 85px; height: 85px; object-fit: cover;" alt="">
                <div>
                    <h4 class="fw-bold text-primary mb-2">${item.fields.first_name} ${item.fields.last_name}</h4>
                    <p class="text-muted">${item.fields.bio}</p>
                </div>
            </li>
        `).join('');
        // Aktualizacja elementów paginacji
        document.querySelector('.pagination').innerHTML = data.pagination;
    }

    // Funkcja do aktualizacji interfejsu użytkownika dla klientów
    function updateClientsUI(data) {
        const container = document.querySelector('#clients-container');
        // Generowanie kodu HTML dla listy klientów
        container.innerHTML = JSON.parse(data.clients).map(item => `
            <li class="list-group-item d-flex align-items-center p-4 mb-4 shadow-lg rounded border-0">
                <img src="${item.fields.photo || '/static/images/Icon_2.png'}" class="rounded-circle me-4 border border-primary" style="width: 85px; height: 85px; object-fit: cover;" alt="">
                <div>
                    <h4 class="fw-bold text-primary mb-2">${item.fields.company_name}</h4>
                    <p class="text-muted">${item.fields.bio}</p>
                </div>
            </li>
        `).join('');
        // Aktualizacja elementów paginacji
        document.querySelector('.pagination').innerHTML = data.pagination;
    }

    // Delegowanie zdarzeń dla linków paginacji
    document.body.addEventListener('click', function (event) {
        if (event.target.classList.contains('pagination-link')) {
            event.preventDefault();
            const type = window.location.href.includes('recruiters') ? 'recruiters' : 'clients';
            fetchResults(event.target.href, type);
        }
    });
});

// Oczekiwanie na pełne załadowanie DOM
document.addEventListener('DOMContentLoaded', function () {

    // Funkcja do pobierania zadań za pomocą żądania AJAX
    function fetchTasks(url) {
        fetch(url, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
            .then(response => response.json()) // Konwersja odpowiedzi na JSON
            .then(data => {
                const tbody = document.querySelector('table tbody');
                // Generowanie kodu HTML dla listy zadań
                tbody.innerHTML = data.tasks.map(task => `
                    <tr>
                        <td><a href="/accounts/task/${task.id}/detail">${task.title}</a></td>
                        <td>${task.description}</td>
                        <td>${task.priority}</td>
                        <td>${task.status}</td>
                        <td>${task.due_date}</td>
                        <td>
                            <a href="/accounts/task/${task.id}/edit/" class="btn btn-warning btn-sm me-1">Edit</a>
                            <a href="/accounts/task/${task.id}/delete/" class="btn btn-danger btn-sm">Delete</a>
                        </td>
                    </tr>
                `).join('');
                // Aktualizacja elementów paginacji
                document.querySelector('.pagination').innerHTML = data.pagination;
            });
    }

    // Delegowanie zdarzeń dla linków paginacji
    document.body.addEventListener('click', function (event) {
        if (event.target.classList.contains('pagination-link')) {
            event.preventDefault();
            fetchTasks(event.target.href);
        }
    });
});
