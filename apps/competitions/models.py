from django.db import models
from django.core.exceptions import ValidationError

class CompetitionType(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ['code']

    def __str__(self):
        return self.name


class Affiliation(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='affiliations/', blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Location(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=300)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
    
class StatusCompetition(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Competition(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    competition_type = models.ForeignKey(CompetitionType, on_delete=models.PROTECT, related_name="competitions")
    status = models.ForeignKey(StatusCompetition, on_delete=models.PROTECT, related_name="competitions")
    affiliation = models.ForeignKey(Affiliation, on_delete=models.PROTECT, related_name="competitions")
    location = models.ForeignKey(Location, on_delete=models.PROTECT, related_name="competitions")
    year = models.PositiveIntegerField(editable=False)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    slug = models.SlugField(unique=True)
    
    def clean(self):
        if self.end_date and self.end_date < self.start_date:
            raise ValidationError({
                "end_date": "La fecha de fin no puede ser anterior a la fecha de inicio."
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        self.year = self.start_date.year
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-start_date", "name"]

    def __str__(self):
        return self.name
