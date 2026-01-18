import csv
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from .models import Grievance


@staff_member_required
def grievance_state_report(request):
    data = (
        Grievance.objects
        .values('state')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    return HttpResponse(data)


@staff_member_required
def export_state_report_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="state_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['State', 'Total Grievances'])

    data = (
        Grievance.objects
        .values('state')
        .annotate(count=Count('id'))
    )

    for row in data:
        writer.writerow([row['state'], row['count']])

    return response
