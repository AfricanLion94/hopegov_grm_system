from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import json
from .models import Grievance, GrievanceAttachment
from django.shortcuts import render, redirect  # Added for render() and redirect()
from django.db.models import Count  # For public_dashboard_view
import pandas as pd
import calendar

@csrf_exempt
def submit_grievance(request):
    if request.method == "POST":
        try:
            # Parse form data
            full_name = request.POST.get('full_name')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            state = request.POST.get('state')
            lga = request.POST.get('lga')
            category = request.POST.get('category')
            description = request.POST.get('description')

            # Validate required fields
            if not all([full_name, phone, state, category, description]):
                return JsonResponse({"error": "Missing required fields"}, status=400)

            # Create grievance
            grievance = Grievance.objects.create(
                full_name=full_name,
                email=email,
                phone=phone,
                state=state,
                lga=lga,
                category=category,
                description=description,
            )

            # Handle file upload if present
            if request.FILES.get('evidence'):
                attachment = GrievanceAttachment.objects.create(
                    grievance=grievance,
                    file=request.FILES['evidence']
                )

            # Redirect to success page with ticket number (no more JSON)
            return redirect(f'/submission-success/?ticket={grievance.ticket_number}')
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid request method"}, status=405)

def track_grievance(request, ticket_number):
    try:
        grievance = Grievance.objects.get(ticket_number=ticket_number)
        return JsonResponse({
            "ticket_number": grievance.ticket_number,
            "status": grievance.status,
            "category": grievance.category,
            "updated_at": grievance.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        })
    except Grievance.DoesNotExist:
        return JsonResponse({"error": "Ticket not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def public_dashboard(request):
    try:
        total = Grievance.objects.count()
        resolved = Grievance.objects.filter(status="Resolved").count()
        pending = Grievance.objects.filter(status="Pending").count()
        return JsonResponse({
            "total": total,
            "resolved": resolved,
            "pending": pending,
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def public_dashboard_view(request):
    # Reuse the same logic as the admin dashboard, but without export
    # ========== FILTERS ==========
    state = request.GET.get("state", "")
    category = request.GET.get("category", "")
    status = request.GET.get("status", "")
    month = request.GET.get("month", "")
    year = request.GET.get("year", "")

    qs = Grievance.objects.all()

    filtered_qs = qs
    if state:
        filtered_qs = filtered_qs.filter(state=state)
    if category:
        filtered_qs = filtered_qs.filter(category=category)
    if status:
        filtered_qs = filtered_qs.filter(status=status)
    if month:
        filtered_qs = filtered_qs.filter(created_at__month=int(month))
    if year:
        filtered_qs = filtered_qs.filter(created_at__year=int(year))

    # ========== KPIs ==========
    kpis = {
        "Total": filtered_qs.count(),
        "New": filtered_qs.filter(status="Pending").count(),
        "InProgress": filtered_qs.filter(status="In Progress").count(),
        "Resolved": filtered_qs.filter(status="Resolved").count(),
        "Closed": filtered_qs.filter(status="Closed").count(),
    }

    # ========== CATEGORY ==========
    categories = list(filtered_qs.values_list("category", flat=True).distinct())
    category_labels = categories
    category_counts = [filtered_qs.filter(category=c).count() for c in categories]

    # ========== STATUS ==========
    status_labels = ["Pending", "In Progress", "Resolved", "Closed"]
    status_counts = [filtered_qs.filter(status=s).count() for s in status_labels]

    # ========== STATES ==========
    states_for_dropdown = sorted(list(Grievance.objects.values_list("state", flat=True).distinct()))
    states_for_chart = list(filtered_qs.values_list("state", flat=True).distinct())
    state_counts = [filtered_qs.filter(state=s).count() for s in states_for_chart]

    # ========== TIME SERIES ==========
    df = pd.DataFrame(filtered_qs.values("created_at"))
    if not df.empty:
        df["date"] = pd.to_datetime(df["created_at"]).dt.date
        ts = df.groupby("date").size().reset_index(name="count")
        time_series = {"dates": ts["date"].astype(str).tolist(), "counts": ts["count"].tolist()}
    else:
        time_series = {"dates": [], "counts": []}

    # ========== HEATMAP ==========
    heatmap_values = []
    max_val = 0
    for s in states_for_chart:
        row = []
        for c in categories:
            val = filtered_qs.filter(state=s, category=c).count()
            row.append(val)
            max_val = max(max_val, val)
        heatmap_values.append(row)
    heatmap = {"states": states_for_chart, "categories": category_labels, "values": heatmap_values, "max": max_val or 1}

    # ========== SUMMARY TABLES ==========
    table_category = filtered_qs.values("category").annotate(count=Count("id"))
    table_state = filtered_qs.values("state").annotate(count=Count("id"))
    table_status = filtered_qs.values("status").annotate(count=Count("id"))

    # ========== INSIGHT ==========
    insight = "No data available."
    if filtered_qs.exists():
        top_state = filtered_qs.values("state").annotate(c=Count("id")).order_by("-c").first()
        top_category = filtered_qs.values("category").annotate(c=Count("id")).order_by("-c").first()
        insight = f"Most grievances are from {top_state['state']} under {top_category['category']} category."

    # ========== MONTHS / YEARS ==========
    months = [{"num": i, "name": calendar.month_name[i]} for i in range(1, 13)]
    years = [y.year for y in Grievance.objects.dates("created_at", "year")]

    context = {
        "kpis": kpis,
        "category_labels": json.dumps(category_labels),
        "category_counts": json.dumps(category_counts),
        "status_labels": json.dumps(status_labels),
        "status_counts": json.dumps(status_counts),
        "all_states": json.dumps(states_for_chart),
        "states_for_dropdown": states_for_dropdown,
        "state_counts": json.dumps(state_counts),
        "time_series": json.dumps(time_series),
        "heatmap": json.dumps(heatmap),
        "all_categories": category_labels,
        "all_statuses": status_labels,
        "months": months,
        "years": years,
        "selected": {"state": state, "category": category, "status": status, "month": month, "year": year},
        "table_category": table_category,
        "table_state": table_state,
        "table_status": table_status,
        "insight": insight,
        "is_public": True,  # Flag to hide export buttons in template
    }

    return render(request, "grm/public_dashboard.html", context)

# New view for success page
def submission_success(request):
    ticket = request.GET.get('ticket')
    if not ticket:
        return render(request, 'grm/submission-error.html')  # Optional error page
    return render(request, 'grm/submission-success.html', {'ticket_number': ticket})