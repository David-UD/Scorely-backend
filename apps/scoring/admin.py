from django.contrib import admin

from .models import ScoringRule


@admin.register(ScoringRule)
class ScoringRuleAdmin(admin.ModelAdmin):
    list_display = ('competition_edition', 'position', 'points')
    list_filter = ('competition_edition',)
    ordering = ('competition_edition', 'position')
