from django.db import models
import random
import string
import hashlib
from cryptography.fernet import Fernet
from django.conf import settings

if not hasattr(settings, 'SERIAL_ENCRYPTION_KEY'):
    raise ValueError("SERIAL_ENCRYPTION_KEY must be set in settings.py")

fernet = Fernet(settings.SERIAL_ENCRYPTION_KEY)


class SerialNumber(models.Model):
    serial_number = models.CharField(max_length=256, unique=True, editable=False)  
    pin = models.CharField(max_length=256, unique=True, editable=False)
    phone_number = models.CharField(max_length=256, unique=True)

    ghana_card_number = models.CharField(max_length=256, default="UNKNOWN", blank=True, null=True)
    ghana_card_number_hash = models.CharField(max_length=64, unique=True, editable=False, null=True, blank=True)

    university = models.CharField(
        max_length=200,
        default="University of Environment and Sustainable Development"
    )
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)

    # NEW FIELDS with safe defaults
    form_type = models.CharField(max_length=50, default="BSc")  
    date_of_birth = models.DateField(default="2000-01-01")      
    nationality = models.CharField(max_length=100, default="Ghana") 
    is_international = models.BooleanField(default=False)  

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Serial Number Record"
        verbose_name_plural = "Serial Number Records"

    def __str__(self):
        return f"{self.get_serial_decrypted()} ({self.get_full_name()})"

    def get_full_name(self):
        return " ".join(filter(None, [self.first_name, self.middle_name, self.last_name]))

    def is_international_student(self):
        """Check if student is international based on checkbox"""
        return self.is_international

    def generate_serial_number(self):
        """Generate serial number based on student type"""
        max_attempts = 10  
        
        for attempt in range(max_attempts):
            if self.is_international_student():
                serial = f"UESD/I-{''.join(random.choices(string.digits, k=6))}"
            else:
                serial = f"UESD-{''.join(random.choices(string.digits, k=6))}"
            
            exists = SerialNumber.objects.filter(serial_number__isnull=False).exists()
            if not exists:
                return serial
            
            try:
                existing_serials = list(SerialNumber.objects.values_list('serial_number', flat=True))
                encrypted_new = fernet.encrypt(serial.encode()).decode()
                if encrypted_new not in existing_serials:
                    return serial
            except Exception:
                return serial
        
        timestamp = str(int(models.DateTimeField.now().timestamp()))[-4:]
        if self.is_international_student():
            return f"UESD/I-{timestamp}{random.randint(100, 999)}"
        else:
            return f"UESD-{timestamp}{random.randint(100, 999)}"

    @staticmethod
    def generate_pin():
        """Generate PIN """
        max_attempts = 5
        
        for attempt in range(max_attempts):
            pin = ''.join(random.choices(string.digits, k=6))
            
            exists = SerialNumber.objects.filter(pin__isnull=False).exists()
            if not exists:
                return pin
            
            try:
                existing_pins = list(SerialNumber.objects.values_list('pin', flat=True))
                encrypted_new = fernet.encrypt(pin.encode()).decode()
                if encrypted_new not in existing_pins:
                    return pin
            except Exception:
                return pin
        
        return f"{random.randint(100000, 999999)}"

    def save(self, *args, **kwargs):
        if not self.serial_number:
            serial = self.generate_serial_number()
            print(f"DEBUG - Generated serial: {serial}, International: {self.is_international_student()}, Checkbox: {self.is_international}")
            self.serial_number = fernet.encrypt(serial.encode()).decode()
        
        if not self.pin:
            pin = self.generate_pin()
            self.pin = fernet.encrypt(pin.encode()).decode()

        if self.ghana_card_number and not self.ghana_card_number.startswith("gAAAA"):
            self.ghana_card_number = fernet.encrypt(self.ghana_card_number.encode()).decode()
        
        if self.phone_number and not self.phone_number.startswith("gAAAA"):
            self.phone_number = fernet.encrypt(self.phone_number.encode()).decode()

        if self.ghana_card_number:
            try:
                decrypted = fernet.decrypt(self.ghana_card_number.encode()).decode()
                self.ghana_card_number_hash = hashlib.sha256(decrypted.encode()).hexdigest()
            except Exception:
                pass

        if not self.form_type:
            self.form_type = "BSc"
        if not self.date_of_birth:
            self.date_of_birth = "2000-01-01"
        if not self.nationality:
            self.nationality = "Ghana"

        super().save(*args, **kwargs)

    def _decrypt(self, value):
        if not value:
            return None
        try:
            return fernet.decrypt(value.encode()).decode()
        except Exception:
            return value

    def get_serial_decrypted(self):
        return self._decrypt(self.serial_number)

    def get_pin_decrypted(self):
        return self._decrypt(self.pin)

    def get_phone_decrypted(self):
        return self._decrypt(self.phone_number)

    def get_ghana_card_decrypted(self):
        return self._decrypt(self.ghana_card_number)