from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Count
from .models import Grievance  # Removed GrievanceCategory since category is a CharField
import pandas as pd
import json
import calendar
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from django.utils.timezone import localtime

# ================= DASHBOARD VIEW =================
def dashboard(request):
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
        "New": filtered_qs.filter(status="Pending").count(),  # Adjusted to match model
        "InProgress": filtered_qs.filter(status="In Progress").count(),
        "Resolved": filtered_qs.filter(status="Resolved").count(),
        "Closed": filtered_qs.filter(status="Closed").count(),
    }

    # ========== CATEGORY ==========
    # Get distinct categories from the Grievance model (since category is a CharField)
    categories = list(filtered_qs.values_list("category", flat=True).distinct())
    category_labels = categories
    category_counts = [filtered_qs.filter(category=c).count() for c in categories]

    # ========== STATUS ==========
    status_labels = ["Pending", "In Progress", "Resolved", "Closed"]  # Match model
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
    table_category = filtered_qs.values("category").annotate(count=Count("id"))  # Fixed: use "category" not "category__name"
    table_state = filtered_qs.values("state").annotate(count=Count("id"))
    table_status = filtered_qs.values("status").annotate(count=Count("id"))

    # ========== INSIGHT ==========
    insight = "No data available."
    if filtered_qs.exists():
        top_state = filtered_qs.values("state").annotate(c=Count("id")).order_by("-c").first()
        top_category = filtered_qs.values("category").annotate(c=Count("id")).order_by("-c").first()  # Fixed: use "category" not "category__name"
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
    }

    return render(request, "grm/dashboard.html", context)

def export_csv(request):
    qs = Grievance.objects.all()
    df = pd.DataFrame(qs.values())
    response = HttpResponse(df.to_csv(index=False), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="grievances.csv"'
    return response

def export_excel(request):
    qs = Grievance.objects.all()
    df = pd.DataFrame(qs.values())

    for col in df.select_dtypes(include=['datetime64[ns, UTC]']).columns:
        df[col] = df[col].apply(lambda x: x.tz_localize(None) if x.tzinfo else x)
    
    wb = Workbook()
    ws = wb.active
    for r in dataframe_to_rows(df, index=False, header=True):
        ws.append(r)

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="grievances.xlsx"'
    wb.save(response)
    return response