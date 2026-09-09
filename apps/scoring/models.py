from django.db import models


class ScoringRule(models.Model):
    competition_edition = models.ForeignKey(
        'competitions.CompetitionEdition',
        on_delete=models.CASCADE,
        related_name='scoring_rules',
    )
    position = models.PositiveIntegerField()
    points = models.PositiveIntegerField()

    class Meta:
        unique_together = ('competition_edition', 'position')
        ordering = ['competition_edition', 'position']

    def __str__(self):
        return f"{self.competition_edition} - Pos {self.position}: {self.points} pts"
