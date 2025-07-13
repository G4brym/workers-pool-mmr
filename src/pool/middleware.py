from django_cf.middleware import CloudflareAccessMiddleware
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomCloudflareAccessMiddleware(CloudflareAccessMiddleware):
    def _get_or_create_user(self, email, name):
        # Your custom user creation logic here
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email,
                'first_name': name.split(' ')[0] if name else '',
                'last_name': ' '.join(name.split(' ')[1:]) if name else '',
                'is_active': True,
                'is_staff': True,
                'is_superuser': True,
            }
        )
        return user
