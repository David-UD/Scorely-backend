from django.contrib import admin

from .models import Competitor, Person, Team, TeamMember


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'birth_date', 'gender', 'affiliation')
    search_fields = ('first_name', 'last_name')
    list_filter = ('gender',)
    autocomplete_fields = ('affiliation',)


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'competition_edition', 'competition_enabled_category', 'affiliation')
    search_fields = ('name',)
    autocomplete_fields = ('competition_edition', 'competition_enabled_category', 'affiliation')


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('team', 'person')
    autocomplete_fields = ('team', 'person')


@admin.register(Competitor)
class CompetitorAdmin(admin.ModelAdmin):
    list_display = ('registration_number', 'competitor_type', 'person', 'team', 'competition_edition')
    list_filter = ('competitor_type', 'competition_edition')
    search_fields = ('registration_number',)
    autocomplete_fields = ('competition_edition', 'person', 'team', 'competition_enabled_category')
