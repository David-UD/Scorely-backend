from django.contrib import admin

from .models import Athlete, Competitor, Team, TeamMember


@admin.register(Athlete)
class AthleteAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'birth_date', 'gender', 'affiliation')
    search_fields = ('first_name', 'last_name')
    list_filter = ('gender',)
    autocomplete_fields = ('affiliation',)


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'affiliation')
    search_fields = ('name',)
    autocomplete_fields = ('affiliation',)


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('team', 'athlete')
    autocomplete_fields = ('team', 'athlete')


@admin.register(Competitor)
class CompetitorAdmin(admin.ModelAdmin):
    list_display = ('registration_number', 'competitor_type', 'athlete', 'team', 'competition')
    list_filter = ('competitor_type', 'competition')
    search_fields = ('registration_number',)
    autocomplete_fields = ('competition', 'athlete', 'team', 'enabled_competition_category')