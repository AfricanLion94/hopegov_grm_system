from django.urls import path
from .dashboard import dashboard, export_csv, export_excel
from .view_public import submit_grievance, track_grievance, public_dashboard, public_dashboard_view, submission_success  # Added submission_success

urlpatterns = [
    # Admin dashboard
    path("dashboard/", dashboard, name="dashboard"),
    path("export/csv/", export_csv, name="export_csv"),
    path("export/excel/", export_excel, name="export_excel"),

    # Public API endpoints
    path("api/grievances/create/", submit_grievance, name="submit_grievance"),
    path("api/grievances/track/<str:ticket_number>/", track_grievance, name="track_grievance"),
    path("api/dashboard/public/", public_dashboard, name="public_dashboard"),
    path("public-dashboard/", public_dashboard_view, name="public_dashboard_view"),
    path("submission-success/", submission_success, name="submission_success"),  # Added this line
]

