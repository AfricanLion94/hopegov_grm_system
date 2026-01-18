from django.contrib import admin
from .models import Grievance, GrievanceAttachment

@admin.register(Grievance)
class GrievanceAdmin(admin.ModelAdmin):
    list_display = ('ticket_number', 'full_name', 'state', 'lga', 'category', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'category', 'state', 'lga')
    search_fields = ('ticket_number', 'full_name', 'email', 'phone')
    readonly_fields = ('ticket_number', 'created_at', 'updated_at')

@admin.register(GrievanceAttachment)
class GrievanceAttachmentAdmin(admin.ModelAdmin):
    list_display = ('grievance', 'file', 'uploaded_at')
    readonly_fields = ('uploaded_at',)