from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SerialNumber
from bankreports.models import DailyFormSale
from django.utils import timezone

@receiver(post_save, sender=SerialNumber)
def log_daily_form_sale(sender, instance, created, **kwargs):
    if created:
        try:
            DailyFormSale.objects.create(
                serial_ref=instance.id,
                first_name=instance.first_name,
                middle_name=instance.middle_name,
                last_name=instance.last_name,
                form_type=instance.form_type,
                is_international=instance.is_international,
                timestamp=timezone.now()
            )
        except Exception as e:
            print(f"DEBUG - Failed to log DailyFormSale: {e}")
