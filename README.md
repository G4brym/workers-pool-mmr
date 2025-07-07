# SnookerSkillz

SnookerSkillz is a Django application for tracking snooker pool matches and player MMR (Matchmaking Rating) rankings, deployed on Cloudflare Workers with a Cloudflare D1 serverless SQL database. It features a TV-optimized landing page displaying recent matches and top players, with data managed via the Django admin interface.

[![Deploy to Cloudflare](https://deploy.workers.cloudflare.com/button)](https://deploy.workers.cloudflare.com/?url=https://github.com/G4brym/snookerskillz)

## Features

- **MMR Tracking**: Players start at 2000 MMR. Supports 1v1, 2v1, and 2v2 matches with fixed MMR adjustments (50 MMR total per ranked match).
- **Match Formats**: Best of 1 (BO1), Best of 3 (BO3), and Best of 5 (BO5), with final scores recorded via Django admin.
- **Friendly Matches**: Record scores without affecting MMR.
- **TV-Optimized Landing Page**: Shows 5 recent matches (left) and top 10 players by MMR with match counts (right), auto-refreshing every 2 minutes using HTMX.
- **Admin Interface**: Manage players and matches through a customized Django admin dashboard.
- **Cloudflare Deployment**: Runs on Cloudflare Workers with D1 database integration via `django-cf`.

## Setup

### Installation

1. **Install Dependencies**:
   ```bash
   npm install
   npm run dependencies
   ```

## Deployment

1. **Deploy to Cloudflare**:
   ```bash
   npx wrangler deploy
   ```

2. **Access the App**:
   - **Landing Page**: `https://your-worker.workers.dev/`
   - **Admin Interface**: `https://your-worker.workers.dev/admin/`

## Usage

- **Admin Interface**: Add players and record matches at `/admin/`. Supports 1v1, 2v1, and 2v2 matches in BO1, BO3, or BO5 formats. Mark matches as ranked or friendly.
- **Landing Page**: Displays 5 recent matches (left) and top 10 players by MMR with match counts (right), optimized for large TV screens, auto-refreshing every 2 minutes.
- **MMR Rules**:
  - Players start at 2000 MMR.
  - Ranked matches: 50 MMR total (e.g., 1v1: winner +50, loser -50; 2v2: each winner +25, each loser -25).
  - Friendly matches: No MMR changes.
  - MMR updates are handled in the `SnookerSkillzMatch` model's `save` method, preventing double-counting on updates.

## Notes

- **D1 Limitations**: No transactions; queries commit immediately. The app ensures MMR consistency.
- **Security**: Protect Cloudflare API tokens and admin credentials.
- **Local Testing**: Use `npx wrangler dev --remote` to test with the live D1 database.
- **Static Files**: Served from `staticfiles/static` via Cloudflare Workers.

---

*See [django-cf](https://github.com/G4brym/django-cf) and [Cloudflare D1](https://developers.cloudflare.com/d1/) for more details.*
