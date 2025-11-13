from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db import IntegrityError
from django.utils import timezone
from .models import SerialNumber
from bankreports.models import DailyFormSale  

def home(request):
    return render(request, 'serialgenerator/home.html')


def validate_serial_ajax(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method.'}, status=405)

    first_name = request.POST.get('first_name', '').strip()
    middle_name = request.POST.get('middle_name', '').strip() or None
    last_name = request.POST.get('last_name', '').strip()
    phone_number = request.POST.get('phone_number', '').strip()
    ghana_card = request.POST.get('ghana_card_number', '').strip()
    nationality = request.POST.get('nationality', 'Ghana').strip()
    international_student = request.POST.get('international_student') == 'on'

    if not first_name or not last_name or not phone_number or not ghana_card:
        return JsonResponse({'error': 'Please fill in all required fields.'}, status=400)

    return JsonResponse({'message': 'Validated successfully.'})


def generate_serial(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        middle_name = request.POST.get('middle_name', '').strip() or None
        last_name = request.POST.get('last_name', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        ghana_card = request.POST.get('ghana_card_number', '').strip()
        form_type = request.POST.get('form_type', '').strip() or ''
        date_of_birth = request.POST.get('date_of_birth', '').strip() or ''
        nationality = request.POST.get('nationality', 'Ghana').strip()
        international_student = request.POST.get('international_student') == 'on'

        print(f"DEBUG - International checkbox: {international_student}")
        print(f"DEBUG - Nationality: {nationality}")

        if not first_name or not last_name or not phone_number or not ghana_card:
            return JsonResponse({'error': 'Please fill in all required fields.'}, status=400)

        try:
            print("DEBUG - Creating new serial record...")
            serial = SerialNumber.objects.create(
                first_name=first_name,
                middle_name=middle_name,
                last_name=last_name,
                phone_number=phone_number,
                ghana_card_number=ghana_card,
                form_type=form_type,
                date_of_birth=date_of_birth,
                nationality=nationality,
                is_international=international_student
            )

            decrypted_serial = serial.get_serial_decrypted()
            print(f"DEBUG - Final serial generated: {decrypted_serial}")

            DailyFormSale.objects.create(
                serial_ref=serial.id,
                form_type=form_type or "General",
                is_international=international_student,
                timestamp=timezone.now()
            )
            print("DEBUG - Recorded form sale in DailyFormSale ")

            return JsonResponse({'redirect_url': f"/success/{serial.id}/"})

        except IntegrityError as e:
            print(f"DEBUG - IntegrityError: {e}")
            return JsonResponse({'error': 'Database integrity error occurred.'}, status=400)
        except Exception as e:
            print(f"DEBUG - General error during creation: {e}")
            return JsonResponse({'error': f'Error creating serial: {str(e)}'}, status=400)

    return render(request, 'serialgenerator/generate.html')


def success(request, serial_id):
    serial = get_object_or_404(SerialNumber, id=serial_id)

    def safe_decrypt(method):
        try:
            result = method() if callable(method) else method
            return result
        except Exception as e:
            print(f"DEBUG - Decryption failed: {e}")
            return 'N/A'

    is_international = serial.is_international_student()

    context = {
        'serial_number': safe_decrypt(serial.get_serial_decrypted),
        'pin': safe_decrypt(serial.get_pin_decrypted),
        'full_name': serial.get_full_name() or '',
        'first_name': serial.first_name or '',
        'middle_name': serial.middle_name or '',
        'last_name': serial.last_name or '',
        'phone_number': safe_decrypt(serial.get_phone_decrypted),
        'id_number': safe_decrypt(serial.get_ghana_card_decrypted),
        'university': getattr(serial, 'university', 'University of Environment and Sustainable Development'),
        'form_type': getattr(serial, 'form_type', '') or '—',
        'date_of_birth': getattr(serial, 'date_of_birth', '') or '—',
        'nationality': getattr(serial, 'nationality', 'Ghana'),
        'is_international': is_international,
        'course_type': getattr(serial, 'form_type', 'Regular'),
    }

    return render(request, 'serialgenerator/success.html', context)
