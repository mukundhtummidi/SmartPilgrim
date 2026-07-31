from django.db import models
from temples.models import Temple

class Festival(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField()
    impact_level = models.CharField(max_length=10, choices=[('HIGH', 'High'), ('MEDIUM', 'Medium')], default='HIGH')

    def __cl__ (self):
        return f"{self.name} ({self.date})"

class PublicHoliday(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField(unique=True)

    def __str__(self):
        return self.name

class CrowdOverride(models.Model):
    LEVEL_CHOICES = [('LOW', 'Low'), ('MEDIUM', 'Medium'), ('HIGH', 'High')]
    
    temple = models.ForeignKey(Temple, on_delete=models.CASCADE)
    date = models.DateField()
    override_level = models.CharField(max_length=10, choices=LEVEL_CHOICES)
    reason = models.CharField(max_length=255)

    class Meta:
        unique_together = ('temple', 'date')

    def __str__(self):
        return f"Override for {self.temple.name} on {self.date}"