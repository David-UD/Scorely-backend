from django.contrib import admin

from .models import (
    CompetitionCategory,
    EnabledCompetitionCategory,
    Event,
    EventCompetitor,
)


@admin.register(CompetitionCategory)
class CompetitionCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'min_members', 'max_members')
    search_fields = ('name',)


@admin.register(EnabledCompetitionCategory)
class EnabledCompetitionCategoryAdmin(admin.ModelAdmin):
    list_display = ('competition', 'competition_category', 'finalist_slots')
    search_fields = ('competition__name', 'competition_category__name')
    autocomplete_fields = ('competition', 'competition_category')


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'event_number', 'competition', 'phase', 'is_ascending', 'is_active')
    list_filter = ('phase', 'is_ascending', 'is_active')
    search_fields = ('name', 'workout')
    autocomplete_fields = ('competition',)


@admin.register(EventCompetitor)
class EventCompetitorAdmin(admin.ModelAdmin):
    list_display = ('competitor', 'event', 'result', 'event_rank', 'score')
    list_filter = ('event',)
    autocomplete_fields = ('competitor', 'event')