
import logging
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

logger = logging.getLogger(__name__)


def send_activation_email(user, request=None):

    try:
        # Generate activation token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # Build activation URL dynamically
        if request:
            activation_link = request.build_absolute_uri(
                f"/accounts/activate/{uid}/{token}/"
            )
        else:
            domain = getattr(settings, 'SITE_DOMAIN', 'http://127.0.0.1:8000')
            activation_link = f"{domain}/accounts/activate/{uid}/{token}/"
        
        # Render email template
        html_content = render_to_string(
            "accounts/activation_email.html",
            {
                "user": user,
                "activation_link": activation_link,
            },
        )
        text_content = strip_tags(html_content)
        
        # Send email
        email = EmailMultiAlternatives(
            subject="Kích hoạt tài khoản - ToDo App",
            body=text_content,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
            to=[user.email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
        
        logger.info(f"Activation email sent successfully to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send activation email to {user.email}: {str(e)}")
        return False


def get_user_from_uidb64(uidb64):

    from django.utils.http import urlsafe_base64_decode
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
        return user
    except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
        logger.warning(f"Invalid uidb64 or user not found: {str(e)}")
        return None

