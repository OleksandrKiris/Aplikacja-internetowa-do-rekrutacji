import os

# Set up Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kirismor.settings")
import django

django.setup()

from django.utils import timezone
from news.models import News

news_items = [
    {
        'title': 'Nowe stanowiska w branży IT',
        'content': 'Szukamy kandydatów na stanowiska programistyczne, '
                   'w tym Python Developer, Java Developer, Frontend Developer.',
        'role': 'candidate'
    },
    {
        'title': 'Rozwijaj swoją firmę z nowymi klientami',
        'content': 'Nasza platforma pomaga firmom w szybkim nawiązywaniu kontaktów '
                   'z potencjalnymi klientami na rynku.',
        'role': 'client'
    },
    {
        'title': 'Znajdź idealnych kandydatów dla swojej firmy',
        'content': 'Skorzystaj z naszych narzędzi do rekrutacji, aby znaleźć '
                   'najlepszych specjalistów w branży.',
        'role': 'recruiter'
    },
    {
        'title': 'Doskonałe oferty pracy dla kandydata',
        'content': 'Odkryj najnowsze oferty w różnych branżach, '
                   'w tym IT, finanse, marketing.',
        'role': 'candidate'
    },
    {
        'title': 'Klienci potrzebują usług twojej firmy',
        'content': 'Zgłoś swoją firmę na naszej platformie, '
                   'aby pozyskać nowych klientów w regionie.',
        'role': 'client'
    },
    {
        'title': 'Poszukujesz najlepszych kandydatów?',
        'content': 'Nasz zespół pomoże ci znaleźć najlepszych specjalistów '
                   'w krótkim czasie.',
        'role': 'recruiter'
    },
    {
        'title': 'Szkolenia dla kandydatów na nowych stanowiskach',
        'content': 'Zapisz się na szkolenia, aby zdobyć umiejętności potrzebne '
                   'do objęcia nowych stanowisk.',
        'role': 'candidate'
    },
    {
        'title': 'Nowe narzędzia dla rekruterów',
        'content': 'Poznaj nowe narzędzia, które pomogą ci znaleźć '
                   'idealnych kandydatów dla twojej firmy.',
        'role': 'recruiter'
    },
    {
        'title': 'Nowe strategie marketingowe dla firm',
        'content': 'Dowiedz się, jak nowe strategie marketingowe mogą pomóc '
                   'w zdobywaniu klientów.',
        'role': 'client'
    }
]

# Populate the News model
for item in news_items:
    News.objects.create(
        title=item['title'],
        content=item['content'],
        date_posted=timezone.now(),
        role=item['role']
    )

print("News items have been successfully added.")
