from django.db import models
import uuid

class GrievanceCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Grievance(models.Model):
    CATEGORY_CHOICES = [
        ("Community Health & Safety", "Community Health & Safety"),
        ("GBV / SEA / SH", "GBV / SEA / SH"),
        ("Labour", "Labour"),
        ("Social", "Social"),
        ("Environmental", "Environmental"),
    ]

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("In Progress", "In Progress"),
        ("Resolved", "Resolved"),
        ("Closed", "Closed"),
    ]

    ticket_number = models.CharField(max_length=50, unique=True, editable=False)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20)
    state = models.CharField(max_length=100)
    lga = models.CharField(max_length=100, blank=True, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            self.ticket_number = f"GRM-{self.created_at.year if self.created_at else 2026}-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.ticket_number

class GrievanceAttachment(models.Model):
    grievance = models.ForeignKey(Grievance, related_name='attachments', on_delete=models.CASCADE)
    file = models.FileField(upload_to='grievance_attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment for {self.grievance.ticket_number}"