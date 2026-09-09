from django.contrib import admin

from .models import Affiliation, Competition, CompetitionEdition, CompetitionType, Location


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


@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = ('name', 'competition_type', 'affiliation', 'location')
    search_fields = ('name',)
    list_filter = ('competition_type',)
    autocomplete_fields = ('competition_type', 'affiliation', 'location')


@admin.register(CompetitionEdition)
class CompetitionEditionAdmin(admin.ModelAdmin):
    list_display = ('competition', 'year', 'start_date', 'end_date', 'status')
    list_filter = ('status', 'year')
    search_fields = ('competition__name',)
    autocomplete_fields = ('competition',)
