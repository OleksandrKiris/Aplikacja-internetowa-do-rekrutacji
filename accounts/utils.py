import time
from django.core.mail import send_mail
from django.conf import settings
from django.utils.translation import gettext as _

"""
Imports explanation:

1. import time
   - Moduł czasu wbudowany w Pythona.
   - Używany do dodania opóźnienia przed wysłaniem emaila.

2. from django.core.mail import send_mail
   - Funkcja Django do wysyłania emaili.
   - Używana do wysyłania emaili za pomocą skonfigurowanych ustawień SMTP.

3. from django.conf import settings
   - Moduł ustawień Django.
   - Używany do uzyskiwania dostępu do ustawień konfiguracyjnych projektu, takich jak adres URL witryny i dane SMTP.

4. from django.utils.translation import gettext as _
   - Funkcja Django do tłumaczenia tekstu.
   - Używana do internacjonalizacji i tłumaczenia tekstu w aplikacjach Django.
"""


def send_verification_email(user):
    """
    Wysyła email weryfikacyjny do użytkownika.

    Generuje token weryfikacyjny, zapisuje go w bazie danych i wysyła email z linkiem weryfikacyjnym do użytkownika.

    Args:
        user (User): Obiekt użytkownika, do którego ma być wysłany email weryfikacyjny.
    """
    token = user.generate_verification_token()
    user.verification_token = token
    user.save()

    verification_link = f"{settings.SITE_URL}/accounts/verify/{token}/"
    subject = _('Zweryfikuj swój email')
    message = _('Kliknij link, aby zweryfikować swój email: {verification_link}').format(
        verification_link=verification_link)
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [user.email]

    time.sleep(2)  # Dodaj niewielkie opóźnienie przed wysłaniem emaila

    send_mail(subject, message, from_email, recipient_list, fail_silently=False)
