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


class CompetitionEnabledCategory(models.Model):
    competition_edition = models.ForeignKey(
        'competitions.CompetitionEdition',
        on_delete=models.CASCADE,
        related_name='enabled_categories',
    )
    competition_category = models.ForeignKey(
        CompetitionCategory,
        on_delete=models.CASCADE,
        related_name='enabled_in_editions',
    )

    class Meta:
        unique_together = ('competition_edition', 'competition_category')
        ordering = ['competition_category']

    def __str__(self):
        return f"{self.competition_edition} - {self.competition_category}"


class CompetitionStage(models.Model):
    class StageType(models.TextChoices):
        QUALIFIER = 'QUALIFIER', 'Qualifier'
        FINAL = 'FINAL', 'Final'

    competition_edition = models.ForeignKey(
        'competitions.CompetitionEdition',
        on_delete=models.CASCADE,
        related_name='stages',
    )
    stage_type = models.CharField(max_length=20, choices=StageType.choices)
    qualification_count = models.PositiveIntegerField(default=0)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.competition_edition} - {self.get_stage_type_display()}"

    def clean(self):
        existing = CompetitionStage.objects.filter(
            competition_edition=self.competition_edition,
            stage_type=self.stage_type,
        )
        if self.pk:
            existing = existing.exclude(pk=self.pk)
        if existing.exists():
            raise ValidationError(f"Only one {self.stage_type} stage allowed per edition.")


class EventResultType(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=50)

    class Meta:
        ordering = ['code']

    def __str__(self):
        return self.code


class RankDirection(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=50)

    class Meta:
        ordering = ['code']

    def __str__(self):
        return self.code


class Event(models.Model):
    competition_stage = models.ForeignKey(
        CompetitionStage,
        on_delete=models.CASCADE,
        related_name='events',
    )
    event_number = models.PositiveIntegerField()
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    event_result_type = models.ForeignKey(EventResultType, on_delete=models.PROTECT)
    rank_direction = models.ForeignKey(RankDirection, on_delete=models.PROTECT)

    class Meta:
        unique_together = ('competition_stage', 'event_number')
        ordering = ['event_number']

    def __str__(self):
        return f"{self.name} (#{self.event_number})"


class StatusEventCompetitor(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=50)

    class Meta:
        ordering = ['code']

    def __str__(self):
        return self.code


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
    status = models.ForeignKey(StatusEventCompetitor, on_delete=models.PROTECT)

    class Meta:
        unique_together = ('competitor', 'event')
        ordering = ['event', 'event_rank']

    def __str__(self):
        return f"{self.competitor} - {self.event}"
