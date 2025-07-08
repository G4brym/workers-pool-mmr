from django.shortcuts import render
from .models import Match, Player
from django.db.models import Count


def landing_page(request):
    # Get the 5 most recent matches
    recent_matches = Match.objects.all().order_by('-date_played')[:5]

    # Get the top 10 players by MMR, annotated with match count
    top_players = Player.objects.annotate(
        match_count=Count('team1_matches_p1') +
                    Count('team1_matches_p2') +
                    Count('team2_matches_p1') +
                    Count('team2_matches_p2')
    ).order_by('-mmr', 'name')[:10]

    top_players = list(top_players)  # Converts to list
    top_players.reverse()  # Reverses the list in Python

    context = {
        'recent_matches': recent_matches,
        'top_players': top_players,
    }

    return render(request, 'index.html', context)
