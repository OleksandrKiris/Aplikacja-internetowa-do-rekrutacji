import time
from django.core.mail import send_mail
from django.conf import settings
from django.utils.translation import gettext as _

"""
Importuje moduł time, który jest używany do dodania opóźnienia przed wysłaniem wiadomości e-mail.

Importuje funkcję send_mail z django.core.mail, która jest używana do wysyłania wiadomości e-mail.

Importuje moduł settings z django.conf, który zawiera ustawienia projektu Django, w tym ustawienia poczty e-mail.

Importuje funkcję gettext jako _, która jest używana do tłumaczenia wiadomości w aplikacji.
"""


def send_verification_email(temp_feedback):
    """
    Wysyła e-mail weryfikacyjny do użytkownika, który pozostawił opinię jako gość.

    - Generuje token weryfikacyjny dla tymczasowej opinii gościa.
    - Zapisuje token w modelu TempGuestFeedback.
    - Tworzy link weryfikacyjny zawierający wygenerowany token.
    - Tworzy temat i treść wiadomości e-mail.
    - Wysyła wiadomość e-mail do użytkownika zawierającą link weryfikacyjny.

    Args:
        temp_feedback (TempGuestFeedback): Instancja modelu TempGuestFeedback, dla której generowany jest token weryfikacyjny.
    """
    token = temp_feedback.generate_verification_token()
    temp_feedback.verification_token = token
    temp_feedback.save()

    verification_link = f"{settings.SITE_URL}/jobs/guest/feedback/verify/{token}/"
    subject = _('Zweryfikuj swój feedback')
    message = _('Kliknij link, aby zweryfikować swój feedback: {verification_link}').format(
        verification_link=verification_link)
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [temp_feedback.email]

    time.sleep(1)  # Dodaje niewielką opóźnienie przed wysłaniem e-maila

    send_mail(subject, message, from_email, recipient_list, fail_silently=False)
