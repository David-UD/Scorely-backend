from django.core.exceptions import ValidationError
from django.db import models


class CompetitionCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    min_members = models.PositiveIntegerField(default=1)
    max_members = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class EnabledCompetitionCategory(models.Model):
    competition = models.ForeignKey(
        'competitions.Competition',
        on_delete=models.CASCADE,
        related_name='enabled_categories',
    )
    competition_category = models.ForeignKey(
        CompetitionCategory,
        on_delete=models.CASCADE,
        related_name='enabled_in_editions',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['competition', 'competition_category'],
                name='unique_enabled_category_per_competition',
            ),
        ]
        ordering = ['competition_category']

    def __str__(self):
        return f"{self.competition} - {self.competition_category}"


class CompetitionStage(models.Model):
    class StageType(models.TextChoices):
        QUALIFIER = 'QUALIFIER', 'Qualifier'
        FINAL = 'FINAL', 'Final'

    competition = models.ForeignKey('competitions.Competition', on_delete=models.CASCADE, related_name='stages')
    stage_type = models.CharField(max_length=20, choices=StageType.choices)
    qualification_count = models.PositiveIntegerField(default=0)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.competition} - {self.get_stage_type_display()}"

    def clean(self):
        existing = CompetitionStage.objects.filter(
            competition=self.competition,
            stage_type=self.stage_type,
        )
        if self.pk:
            existing = existing.exclude(pk=self.pk)
        if existing.exists():
            raise ValidationError(f"Only one {self.stage_type} stage allowed per edition.")


class Event(models.Model):
    name = models.CharField(max_length=200)
    workout = models.TextField()
    description = models.TextField(blank=True)
    competition_stage = models.ForeignKey(CompetitionStage, on_delete=models.CASCADE, related_name='events')
    event_number = models.PositiveIntegerField()
    is_ascending = models.BooleanField(default=False, help_text="Indica si el resultado se ordena de menor a mayor.")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['competition_stage', 'event_number'],
                name='unique_event_number_per_stage',
            ),
        ]
        ordering = ['event_number']
    
    def __str__(self):
        return f"{self.name} (#{self.event_number})"


class EventCompetitor(models.Model):
    competitor = models.ForeignKey(
        'participants.Competitor',
        on_delete=models.CASCADE,
        related_name='event_results',
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='competitors',
    )
    result = models.CharField(max_length=50)
    event_rank = models.PositiveIntegerField(null=True, blank=True)
    score = models.IntegerField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['competitor', 'event'],
                name='unique_competitor_per_event',
            ),
        ]
        ordering = ['event', 'event_rank']

    def __str__(self):
        return f"{self.competitor} - {self.event}"
