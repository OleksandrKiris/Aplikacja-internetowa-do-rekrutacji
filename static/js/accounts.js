document.addEventListener('DOMContentLoaded', function () {
    function fetchResults(url, type) {
        fetch(url, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
            .then(response => response.json())
            .then(data => {
                if (type === 'recruiters') {
                    updateRecruitersUI(data);
                } else if (type === 'clients') {
                    updateClientsUI(data);
                }
            });
    }

    function updateRecruitersUI(data) {
        const container = document.querySelector('#recruiters-container');
        container.innerHTML = JSON.parse(data.recruiters).map(item => `
            <li class="list-group-item d-flex align-items-center p-4 mb-4 shadow-lg rounded border-0">
                <img src="${item.fields.photo || '/static/images/Icon_4.png'}" class="rounded-circle me-4 border border-primary" style="width: 85px; height: 85px; object-fit: cover;" alt="">
                <div>
                    <h4 class="fw-bold text-primary mb-2">${item.fields.first_name} ${item.fields.last_name}</h4>
                    <p class="text-muted">${item.fields.bio}</p>
                </div>
            </li>
        `).join('');
        document.querySelector('.pagination').innerHTML = data.pagination;
    }

    function updateClientsUI(data) {
        const container = document.querySelector('#clients-container');
        container.innerHTML = JSON.parse(data.clients).map(item => `
            <li class="list-group-item d-flex align-items-center p-4 mb-4 shadow-lg rounded border-0">
                <img src="${item.fields.photo || '/static/images/Icon_2.png'}" class="rounded-circle me-4 border border-primary" style="width: 85px; height: 85px; object-fit: cover;" alt="">
                <div>
                    <h4 class="fw-bold text-primary mb-2">${item.fields.company_name}</h4>
                    <p class="text-muted">${item.fields.bio}</p>
                </div>
            </li>
        `).join('');
        document.querySelector('.pagination').innerHTML = data.pagination;
    }

    // Event delegation for pagination links
    document.body.addEventListener('click', function (event) {
        if (event.target.classList.contains('pagination-link')) {
            event.preventDefault();
            const type = window.location.href.includes('recruiters') ? 'recruiters' : 'clients';
            fetchResults(event.target.href, type);
        }
    });
});

    document.addEventListener('DOMContentLoaded', function () {
    function fetchTasks(url) {
        fetch(url, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
            .then(response => response.json())
            .then(data => {
                const tbody = document.querySelector('table tbody');
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
                document.querySelector('.pagination').innerHTML = data.pagination;
            });
    }

    document.body.addEventListener('click', function (event) {
    if (event.target.classList.contains('pagination-link')) {
    event.preventDefault();
    fetchTasks(event.target.href);
}
});
});

