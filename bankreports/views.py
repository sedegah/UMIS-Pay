from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.db.models import Count
from django.utils import timezone
from datetime import datetime, timedelta
from serialgenerator.models import SerialNumber
import csv
from io import StringIO


def report_dashboard(request):
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    if not start_date_str or not end_date_str:
        end_date = timezone.now().date()
        start_date = end_date
    else:
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except ValueError:
            end_date = timezone.now().date()
            start_date = end_date
    
    end_date_with_time = end_date + timedelta(days=1)
    
    sales = SerialNumber.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lt=end_date_with_time
    )

    total_sales = sales.count()
    local_sales = sales.filter(is_international=False).count()
    intl_sales = sales.filter(is_international=True).count()

    breakdown = (
        sales.values('form_type', 'is_international')
        .annotate(total=Count('id'))
        .order_by('form_type')
    )

    detailed_sales = sales.order_by('-created_at')

    context = {
        "start_date": start_date,
        "end_date": end_date,
        "total_sales": total_sales,
        "local_sales": local_sales,
        "intl_sales": intl_sales,
        "breakdown": breakdown,
        "detailed_sales": detailed_sales,
    }

    return render(request, "bankreports/report_dashboard.html", context)


def daily_report_api(request):
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    if not start_date_str or not end_date_str:
        end_date = timezone.now().date()
        start_date = end_date
    else:
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except ValueError:
            return JsonResponse({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)
    
    if start_date > end_date:
        return JsonResponse({"error": "Start date cannot be after end date."}, status=400)
    
    end_date_with_time = end_date + timedelta(days=1)
    
    sales = SerialNumber.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lt=end_date_with_time
    )

    total_sales = sales.count()
    local_sales = sales.filter(is_international=False).count()
    intl_sales = sales.filter(is_international=True).count()

    breakdown = (
        sales.values('form_type', 'is_international')
        .annotate(total=Count('id'))
        .order_by('form_type')
    )

    details = [
        {
            "buyer_name": sn.get_full_name(),
            "form_type": sn.form_type,
            "is_international": sn.is_international,
            "created_at": sn.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }
        for sn in sales.order_by('-created_at')
    ]

    if start_date == end_date:
        date_range_display = start_date.strftime("%b. %d, %Y")
    else:
        date_range_display = f"{start_date.strftime('%b. %d, %Y')} to {end_date.strftime('%b. %d, %Y')}"

    data = {
        "date_range": date_range_display,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "summary": {
            "total_sales": total_sales,
            "local_sales": local_sales,
            "international_sales": intl_sales,
        },
        "breakdown": list(breakdown),
        "details": details,
    }

    return JsonResponse(data)


def export_daily_csv(request):
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    if not start_date_str or not end_date_str:
        end_date = timezone.now().date()
        start_date = end_date
    else:
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except ValueError:
            return HttpResponse("Invalid date format. Use YYYY-MM-DD.", status=400)
    
    if start_date > end_date:
        return HttpResponse("Start date cannot be after end date.", status=400)
    
    end_date_with_time = end_date + timedelta(days=1)
    
    sales = SerialNumber.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lt=end_date_with_time
    ).order_by('-created_at')

    buffer = StringIO()
    writer = csv.writer(buffer)
    
    if start_date == end_date:
        writer.writerow([f"Bank Report - {start_date}"])
    else:
        writer.writerow([f"Bank Report - {start_date} to {end_date}"])
    
    writer.writerow([])
    writer.writerow(["Buyer Name", "Form Type", "International", "Date", "Time"])

    for sale in sales:
        writer.writerow([
            sale.get_full_name(),
            sale.form_type,
            "Yes" if sale.is_international else "No",
            sale.created_at.strftime("%Y-%m-%d"),
            sale.created_at.strftime("%H:%M:%S"),
        ])

    if start_date == end_date:
        filename = f"bankreport_{start_date}.csv"
    else:
        filename = f"bankreport_{start_date}_to_{end_date}.csv"

    response = HttpResponse(buffer.getvalue(), content_type="text/csv")
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response