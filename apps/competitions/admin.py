from django.contrib import admin

from .models import Affiliation, Competition, CompetitionType, Location, StatusCompetition


@admin.register(CompetitionType)
class CompetitionTypeAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    search_fields = ('code', 'name')


@admin.register(Affiliation)
class AffiliationAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'state', 'country')
    search_fields = ('name',)
    list_filter = ('country', 'state')


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'state', 'country')
    search_fields = ('name',)
    list_filter = ('country', 'state')


@admin.register(StatusCompetition)
class StatusCompetitionAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    search_fields = ('code', 'name')


@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = ('name', 'competition_type', 'status', 'affiliation', 'location', 'year', 'start_date')
    list_filter = ('competition_type', 'status', 'year')
    search_fields = ('name',)
    autocomplete_fields = ('competition_type', 'status', 'affiliation', 'location')
