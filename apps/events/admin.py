from django.contrib import admin

from .models import (
    CompetitionCategory,
    CompetitionStage,
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
    list_display = ('competition', 'competition_category')
    search_fields = ('competition__name', 'competition_category__name')
    autocomplete_fields = ('competition', 'competition_category')


@admin.register(CompetitionStage)
class CompetitionStageAdmin(admin.ModelAdmin):
    list_display = ('competition', 'stage_type', 'qualification_count', 'order')
    list_filter = ('stage_type',)
    search_fields = ('competition__name',)
    autocomplete_fields = ('competition',)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'event_number', 'competition_stage', 'is_ascending', 'is_active')
    list_filter = ('is_ascending', 'is_active')
    search_fields = ('name', 'workout')
    autocomplete_fields = ('competition_stage',)


@admin.register(EventCompetitor)
class EventCompetitorAdmin(admin.ModelAdmin):
    list_display = ('competitor', 'event', 'result', 'event_rank', 'score')
    list_filter = ('event',)
    autocomplete_fields = ('competitor', 'event')