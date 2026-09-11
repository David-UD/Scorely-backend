from django.db import models


class ScoringRule(models.Model):
    competition = models.ForeignKey('competitions.Competition',on_delete=models.CASCADE,related_name='scoring_rules')
    position = models.PositiveIntegerField()
    points = models.PositiveIntegerField()

    class Meta:
        unique_together = ('competition', 'position')
        ordering = ['competition', 'position']

    def __str__(self):
        return f"{self.competition} - Pos {self.position}: {self.points} pts"
