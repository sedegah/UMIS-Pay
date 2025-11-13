from django.db import models
from django.utils import timezone

class DailyFormSale(models.Model):
    """
    Stores each successful form purchase for reporting purposes.
    Includes buyer info, form type, international status, and timestamp.
    """

    serial_ref = models.PositiveIntegerField(
        help_text="Reference ID from SerialNumber or transaction record"
    )
    first_name = models.CharField(
        max_length=50, default="Unknown", help_text="Buyer's first name"
    )
    middle_name = models.CharField(
        max_length=50, blank=True, null=True, help_text="Buyer's middle name"
    )
    last_name = models.CharField(
        max_length=50, default="Unknown", help_text="Buyer's last name"
    )
    form_type = models.CharField(
        max_length=50,
        help_text="Type of form sold (e.g., Undergraduate, Postgraduate)"
    )
    is_international = models.BooleanField(
        default=False,
        help_text="True if the buyer is an international student"
    )
    timestamp = models.DateTimeField(
        default=timezone.now,
        help_text="Time when the sale occurred"
    )

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Daily Form Sale"
        verbose_name_plural = "Daily Form Sales"

    def full_name(self):
        """Return full name of the buyer."""
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return (
            f"{self.full_name()} - {self.form_type} "
            f"({'Intl' if self.is_international else 'Local'}) - "
            f"{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
        )
