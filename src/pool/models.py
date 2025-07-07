from django.db import models
from django.core.validators import MinValueValidator


class Player(models.Model):
    name = models.CharField(max_length=100, unique=True)
    mmr = models.IntegerField(default=2000)

    def __str__(self):
        return f"{self.name} ({self.mmr} MMR)"

    class Meta:
        verbose_name = 'Player'
        verbose_name_plural = 'Players'
        ordering = ['-mmr', 'name']


class Match(models.Model):
    MATCH_TYPE_CHOICES = [
        ('1v1', '1 vs 1 Showdown'),
        ('2v1', '2 vs 1 Clash'),
        ('2v2', '2 vs 2 Battle'),
    ]

    MATCH_FORMAT_CHOICES = [
        ('BO1', 'Best of 1 Quickshot'),
        ('BO3', 'Best of 3 Challenge'),
        ('BO5', 'Best of 5 Epic'),
    ]

    match_type = models.CharField(max_length=3, choices=MATCH_TYPE_CHOICES)
    match_format = models.CharField(max_length=3, choices=MATCH_FORMAT_CHOICES)
    is_ranked = models.BooleanField(default=True, verbose_name='Ranked Match')
    date_played = models.DateTimeField(auto_now_add=True)

    # Team 1 players (can be 1 or 2 players)
    team1_player1 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='team1_matches_p1',
                                      verbose_name='Team 1 Player 1')
    team1_player2 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='team1_matches_p2',
                                      null=True, blank=True, verbose_name='Team 1 Player 2')

    # Team 2 players (can be 1 or 2 players)
    team2_player1 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='team2_matches_p1',
                                      verbose_name='Team 2 Player 1')
    team2_player2 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='team2_matches_p2',
                                      null=True, blank=True, verbose_name='Team 2 Player 2')

    # Scores
    team1_score = models.IntegerField(validators=[MinValueValidator(0)], verbose_name='Team 1 Score')
    team2_score = models.IntegerField(validators=[MinValueValidator(0)], verbose_name='Team 2 Score')

    def __str__(self):
        team1 = f"{self.team1_player1.name}"
        if self.team1_player2:
            team1 += f" & {self.team1_player2.name}"
        team2 = f"{self.team2_player1.name}"
        if self.team2_player2:
            team2 += f" & {self.team2_player2.name}"
        return f"{team1} vs {team2} ({self.match_format}, {self.team1_score}-{self.team2_score})"

    def clean(self):
        from django.core.exceptions import ValidationError

        # Validate match type and player counts
        if self.match_type == '1v1':
            if self.team1_player2 or self.team2_player2:
                raise ValidationError("1v1 Showdown matches must have exactly one player per team.")
        elif self.match_type == '2v1':
            if not self.team1_player2 or self.team2_player2:
                raise ValidationError("2v1 Clash matches must have two players on team 1 and one player on team 2.")
        elif self.match_type == '2v2':
            if not self.team1_player2 or not self.team2_player2:
                raise ValidationError("2v2 Battle matches must have two players per team.")

        # Validate scores based on match format
        max_scores = {'BO1': 1, 'BO3': 2, 'BO5': 3}
        max_score = max_scores[self.match_format]
        if self.team1_score + self.team2_score > max_score or max(self.team1_score, self.team2_score) > max_score:
            raise ValidationError(
                f"Scores for {self.match_format} must sum to at most {max_score} and neither team can exceed {max_score}.")

        # Ensure no player is on both teams
        players = {self.team1_player1, self.team1_player2, self.team2_player1, self.team2_player2}
        if None in players:
            players.remove(None)
        if len(players) != len([p for p in players if p is not None]):
            raise ValidationError("A player cannot be on both teams.")

    def apply_mmr_changes(self, team1_score, team2_score, is_ranked, reverse=False):
        """Apply or reverse MMR changes based on match outcome."""
        if not is_ranked:
            return

        multiplier = -1 if reverse else 1
        winner_team = 1 if team1_score > team2_score else 2

        if self.match_type == '1v1':
            if winner_team == 1:
                self.team1_player1.mmr += 50 * multiplier
                self.team2_player1.mmr -= 50 * multiplier
            else:
                self.team1_player1.mmr -= 50 * multiplier
                self.team2_player1.mmr += 50 * multiplier
        elif self.match_type == '2v1':
            if winner_team == 1:
                self.team1_player1.mmr += 25 * multiplier
                self.team1_player2.mmr += 25 * multiplier
                self.team2_player1.mmr -= 50 * multiplier
            else:
                self.team1_player1.mmr -= 25 * multiplier
                self.team1_player2.mmr -= 25 * multiplier
                self.team2_player1.mmr += 50 * multiplier
        elif self.match_type == '2v2':
            if winner_team == 1:
                self.team1_player1.mmr += 25 * multiplier
                self.team1_player2.mmr += 25 * multiplier
                self.team2_player1.mmr -= 25 * multiplier
                self.team2_player2.mmr -= 25 * multiplier
            else:
                self.team1_player1.mmr -= 25 * multiplier
                self.team1_player2.mmr -= 25 * multiplier
                self.team2_player1.mmr += 25 * multiplier
                self.team2_player2.mmr += 25 * multiplier

        # Save updated MMRs
        self.team1_player1.save()
        if self.team1_player2:
            self.team1_player2.save()
        self.team2_player1.save()
        if self.team2_player2:
            self.team2_player2.save()

    def save(self, *args, **kwargs):
        self.clean()

        # Check if this is an update (i.e., the match already exists in the database)
        is_update = self.pk is not None

        if is_update:
            # Fetch the existing match from the database
            try:
                old_match = Match.objects.get(pk=self.pk)
                # Reverse the previous MMR changes if the match was ranked and the outcome or ranked status changed
                if old_match.is_ranked and (
                        old_match.team1_score != self.team1_score or
                        old_match.team2_score != self.team2_score or
                        old_match.is_ranked != self.is_ranked
                ):
                    self.apply_mmr_changes(
                        old_match.team1_score,
                        old_match.team2_score,
                        old_match.is_ranked,
                        reverse=True
                    )
            except Match.DoesNotExist:
                # If the match doesn't exist (shouldn't happen), treat as new
                is_update = False

        # Apply new MMR changes if the match is ranked
        if self.is_ranked:
            self.apply_mmr_changes(self.team1_score, self.team2_score, self.is_ranked)

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Match'
        verbose_name_plural = 'Matches'
        ordering = ['-date_played']
