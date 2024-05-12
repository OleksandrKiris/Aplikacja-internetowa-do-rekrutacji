import os

# Путь к вашему проекту
project_path = '/'
# Список всех пакетов для проверки
packages = [
    "asgiref", "Django", "django-recaptcha", "exceptiongroup", "Faker",
    "iniconfig", "packaging", "pillow", "pluggy", "psycopg2-binary",
    "pytest", "pytest-django", "python-dateutil", "pytz", "six",
    "sqlparse", "tomli", "typing_extensions"
]

used_packages = {pkg: False for pkg in packages}

# Просмотр всех файлов в директории проекта
for subdir, dirs, files in os.walk(project_path):
    for file in files:
        file_path = os.path.join(subdir, file)
        if file_path.endswith('.py'):  # проверяем только Python файлы
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                for pkg in packages:
                    if f'import {pkg}' in content or f'from {pkg} import' in content:
                        used_packages[pkg] = True

# Вывод результатов
for pkg, used in used_packages.items():
    print(f"{pkg}: {'Используется' if used else 'Не используется'}")
