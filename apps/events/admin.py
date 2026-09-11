from django.contrib import admin

from .models import (
    CompetitionCategory,
    CompetitionStage,
    EnabledCompetitionCategory,
    Event,
    EventCompetitor,
    EventResultType,
    RankDirection,
    StatusEventCompetitor,
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


@admin.register(EventResultType)
class EventResultTypeAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    search_fields = ('code', 'name')


@admin.register(RankDirection)
class RankDirectionAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    search_fields = ('code', 'name')


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'event_number', 'competition_stage', 'event_result_type', 'rank_direction')
    list_filter = ('event_result_type', 'rank_direction')
    search_fields = ('name',)
    autocomplete_fields = ('competition_stage', 'event_result_type', 'rank_direction')


@admin.register(StatusEventCompetitor)
class StatusEventCompetitorAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    search_fields = ('code', 'name')


@admin.register(EventCompetitor)
class EventCompetitorAdmin(admin.ModelAdmin):
    list_display = ('competitor', 'event', 'result', 'event_rank', 'score', 'status')
    list_filter = ('status', 'event')
    autocomplete_fields = ('competitor', 'event', 'status')