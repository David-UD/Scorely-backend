from django.contrib import admin

from .models import ScoringRule


@admin.register(ScoringRule)
class ScoringRuleAdmin(admin.ModelAdmin):
    list_display = ('competition', 'position', 'points')
    list_filter = ('competition',)
    ordering = ('competition', 'position')
