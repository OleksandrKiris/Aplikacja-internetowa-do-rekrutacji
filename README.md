# KIRIS M.O.R.

## Opis projektu

KIRIS M.O.R. to zaawansowany system zarządzania rekrutacją, legalizacją i logistyką, zaprojektowany, aby ułatwić i usprawnić procesy zarządzania pracownikami z zagranicy. System integruje kilka kluczowych funkcjonalności w jednej platformie, w tym zarządzanie ofertami pracy, procesami rekrutacji, legalizacją statusu pracowników oraz ich logistyką.

## Główne funkcje

### Aplikacja Accounts
* **Zarządzanie rejestracją i autentykacją:** Użytkownicy mogą rejestrować się i logować używając adresu e-mail.
* **Zarządzanie profilami użytkowników:** Użytkownicy mogą edytować swoje profile, dodawać zdjęcia oraz informacje biograficzne.
* **Role i uprawnienia:** System wspiera różne role użytkowników, takie jak kandydat, pracodawca, czy rekruter, z różnymi poziomami dostępu.

### Aplikacja Jobs
* **Zarządzanie ofertami pracy:** Pracodawcy mogą tworzyć i zarządzać ofertami pracy.
* **Aplikowanie i zarządzanie aplikacjami:** Kandydaci mogą aplikować na oferty, a rekruterzy zarządzać procesem selekcji.

### Aplikacja Requests
* **Zarządzanie zapytaniami o zatrudnienie:** Pracodawcy mogą składać zapytania, które są przetwarzane przez rekruterów.

### Aplikacja Communications
* **Komunikacja wewnętrzna:** System umożliwia wymianę wiadomości między użytkownikami.

## Technologie
* **Backend:** Django
* **Frontend:** React (opcjonalnie)
* **Baza danych:** PostgreSQL
* **Deployment:** Docker

## Instalacja i uruchomienie

Aby zainstalować i uruchomić projekt lokalnie, wykonaj następujące kroki:

### Klonowanie repozytorium

git clone https://github.com/OleksandrKiris/KIRIS_MOR.git
cd /Kirismorr

graphql


### Tworzenie i aktywacja wirtualnego środowiska

python3 -m venv venv
source venv/bin/activate # Na Windows: venv\Scripts\activate


### Instalacja zależności.

pip install -r requirements.txt


### Konfiguracja środowiska
Utwórz plik `.env` w katalogu głównym projektu i dodaj następujące zmienne środowiskowe:

SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_NAME=your_db_name
DATABASE_USER=your_db_user
DATABASE_PASSWORD=your_db_password
DATABASE_HOST=your_db_host
EMAIL_HOST_USER=your_email_user
EMAIL_HOST_PASSWORD=your_email_password

shell


### Migracja bazy danych

python manage.py migrate


### Uruchomienie serwera deweloperskiego

python manage.py runserver


Teraz możesz odwiedzić aplikację w przeglądarce pod adresem `http://localhost:8000`.

