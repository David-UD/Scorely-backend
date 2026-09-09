from django.core.exceptions import ValidationError
from django.db import models


class Person(models.Model):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, blank=True)
    profile_photo = models.ImageField(upload_to='persons/', blank=True, null=True)
    affiliation = models.ForeignKey(
        'competitions.Affiliation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Team(models.Model):
    competition_edition = models.ForeignKey(
        'competitions.CompetitionEdition',
        on_delete=models.CASCADE,
        related_name='teams',
    )
    competition_enabled_category = models.ForeignKey(
        'events.CompetitionEnabledCategory',
        on_delete=models.CASCADE,
        related_name='teams',
    )
    affiliation = models.ForeignKey(
        'competitions.Affiliation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=200)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class TeamMember(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='members')
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='team_memberships')

    class Meta:
        unique_together = ('team', 'person')
        ordering = ['team']

    def __str__(self):
        return f"{self.team.name} - {self.person}"


class Competitor(models.Model):
    class CompetitorType(models.TextChoices):
        INDIVIDUAL = 'INDIVIDUAL', 'Individual'
        TEAM = 'TEAM', 'Team'

    competition_edition = models.ForeignKey(
        'competitions.CompetitionEdition',
        on_delete=models.CASCADE,
        related_name='competitors',
    )
    competitor_type = models.CharField(max_length=20, choices=CompetitorType.choices)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, null=True, blank=True, related_name='competitions')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True, related_name='competitors')
    registration_number = models.CharField(max_length=50, blank=True)
    competition_enabled_category = models.ForeignKey(
        'events.CompetitionEnabledCategory',
        on_delete=models.CASCADE,
        related_name='competitors',
    )

    class Meta:
        ordering = ['registration_number']

    def __str__(self):
        if self.competitor_type == self.CompetitorType.INDIVIDUAL:
            return f"{self.person} ({self.registration_number})"
        return f"{self.team} ({self.registration_number})"

    def clean(self):
        if self.competitor_type == self.CompetitorType.INDIVIDUAL:
            if not self.person:
                raise ValidationError('Person is required for individual competitors.')
            if self.team:
                raise ValidationError('Team must be null for individual competitors.')
        elif self.competitor_type == self.CompetitorType.TEAM:
            if not self.team:
                raise ValidationError('Team is required for team competitors.')
            if self.person:
                raise ValidationError('Person must be null for team competitors.')
