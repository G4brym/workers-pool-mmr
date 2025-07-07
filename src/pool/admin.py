from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group, User
from django.utils.translation import gettext_lazy as _

from .forms import CustomUserCreationForm
from .models import Player, Match

# Customize the admin site
admin.site.site_header = 'SnookerSkillz'
admin.site.site_title = 'SnookerSkillz'
admin.site.index_title = 'Welcome to SnookerSkillz Management'

admin.site.unregister(User)
admin.site.unregister(Group)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {
            'fields': ('is_superuser',),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    readonly_fields = ('last_login', 'date_joined')
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_superuser')
    list_filter = ('is_superuser',)
    filter_horizontal = []


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'mmr')
    search_fields = ('name',)
    ordering = ('-mmr', 'name')
    list_display_links = ('name',)
    list_per_page = 20
    readonly_fields = ('mmr',)


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('get_match_description', 'match_type', 'match_format', 'is_ranked', 'date_played')
    list_filter = ('match_type', 'match_format', 'is_ranked')
    search_fields = ('team1_player1__name', 'team1_player2__name', 'team2_player1__name', 'team2_player2__name')
    date_hierarchy = 'date_played'
    list_per_page = 20

    def get_match_description(self, obj):
        team1 = f"{obj.team1_player1.name}"
        if obj.team1_player2:
            team1 += f" & {obj.team1_player2.name}"
        team2 = f"{obj.team2_player1.name}"
        if obj.team2_player2:
            team2 += f" & {obj.team2_player2.name}"
        return f"{team1} vs {team2} ({obj.team1_score}-{obj.team2_score})"

    get_match_description.short_description = 'Match'
