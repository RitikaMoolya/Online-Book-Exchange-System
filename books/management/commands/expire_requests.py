from django.core.management.base import BaseCommand
from django.utils import timezone
from books.models import ExchangeRequest

class Command(BaseCommand):

    def handle(self, *args, **kwargs):

        expired = ExchangeRequest.objects.filter(
            status__in=["pending","approved"],
            expires_at__lt=timezone.now()
        )


        for r in expired:
            r.status = "expired"
            r.save()
