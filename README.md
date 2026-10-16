# Veer Barmeshwar Sena — Django community platform

A Hindi-first, mobile-friendly community platform for official updates, images, video posts, member comments, likes, shares, and moderation.

## Community features
- Anyone can read published posts without logging in.
- Members can create a free account using a username and password; email is optional. Login accepts username or email plus password. No Google OAuth, paid login provider, or third-party account is required.
- Members must sign in before liking, commenting, or sharing.
- Public registration creates regular member accounts only. It never grants staff or superuser privileges.
- Staff can publish posts, images and videos from the staff dashboard. Django Admin at `/admin/` remains available for full user management and moderation.
- Admin dashboard reports post counts, likes, comments, share actions, reports and recent member activity. Full activity records are available in Django Admin.
- Draft, scheduled, published, and archived post states are supported.
- Posts can be pinned, searched, liked/unliked, commented on, reported and shared.
- Video uploads: MP4, WebM or MOV, up to 50 MB.

## Local setup
Use Python 3.12+.

```bash
python -m venv .venv
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Create the first Render administrator without Shell
The build script supports a temporary, one-time setup using Render Environment variables:

1. Open Render Dashboard → your web service → **Environment**.
2. Add `DJANGO_ADMIN_USERNAME`, `DJANGO_ADMIN_PASSWORD`, and optionally `DJANGO_ADMIN_EMAIL`.
3. Save and wait for a successful deploy. The build runs migrations, then creates the superuser if that username does not already exist.
4. Log in at `https://veer-barmeshwar-sena.onrender.com/admin/`.
5. After successful login, remove all three `DJANGO_ADMIN_*` variables from Render Environment and save. Never put passwords in GitHub or share them in chat.

## Media storage
Render's ordinary web-service filesystem is ephemeral. For reliable long-term media, configure an S3-compatible object-storage bucket in Render Environment:
- `AWS_STORAGE_BUCKET_NAME`
- `AWS_S3_REGION_NAME`
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_S3_ENDPOINT_URL` (optional for compatible providers)

These storage services may have free tiers or usage limits; check the provider's current terms. Without bucket configuration, media is stored on the local filesystem and may be lost when the Render service restarts or redeploys. The website code and login do not require any paid authentication service.

## Tests and checks
```bash
python manage.py test
python manage.py check
python manage.py check --deploy
```

## Production checklist
- Set a strong `SECRET_KEY` in Render Environment.
- Keep `DEBUG=False`, HTTPS, correct hosts and trusted origins.
- Remove temporary `DJANGO_ADMIN_*` variables after initial admin setup.
- Configure SMTP if email-based password reset is needed.
- Back up the production database and test restoration.

## Historical information
The About page provides brief, attributed historical context about Brahmeshwar Singh (“Brahmeshwar Mukhiya”), based on published reporting. The account is intentionally neutral and notes the violence and legal context rather than glorifying caste-based violence. Confirm image permissions before commercial reuse.
