from django.db import models
from django.utils.translation import gettext_lazy as _

"""
Importy:
- from django.db import models: Importuje moduł modeli Django, który pozwala na tworzenie struktur baz danych w Django.
- from django.utils.translation import gettext_lazy as _: Importuje funkcję tłumaczenia, umożliwiającą międzynarodowe tłumaczenie tekstów.
"""


class News(models.Model):
    """
    Model reprezentujący wiadomość.

    Atrybuty:
        title (str): Tytuł wiadomości.
        content (str): Zawartość wiadomości.
        date_posted (DateTime): Data dodania wiadomości.
        role (str): Rola, do której odnosi się wiadomość (kandydat, klient, rekruter).
    """
    title = models.CharField(max_length=200, verbose_name=_("Tytuł"))
    content = models.TextField(verbose_name=_("Zawartość"))
    date_posted = models.DateTimeField(auto_now_add=True, verbose_name=_("Data dodania"))
    role = models.CharField(
        max_length=50,
        choices=[
            ('candidate', _('Kandydat')),
            ('client', _('Klient')),
            ('recruiter', _('Rekruter'))
        ],
        verbose_name=_("Rola")
    )

    def __str__(self):
        """
        Zwraca reprezentację tekstową modelu.

        Returns:
            str: Tytuł wiadomości.
        """
        return self.title
