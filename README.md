# Veer Barmeshwar Sena — Django community platform

A Hindi-first, mobile-friendly community platform for official updates, images, video posts, member comments, likes, shares, and moderation.

## Community features
- Public users can read published posts and videos without logging in.
- Members must sign in before liking, commenting, or sharing. Google sign-in is optional and appears after Google OAuth credentials are configured.
- Staff users can publish posts, images and videos from the staff dashboard. Django Admin at `/admin/` remains available for full user management and moderation.
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
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Enable Google sign-in on Render
Google sign-in is hidden until both environment variables are configured.

1. Open [Google Cloud Console](https://console.cloud.google.com/) and select/create a project.
2. Configure the OAuth consent screen with the app name and contact details. While the app is in testing, add your own Google account as a test user.
3. Create an OAuth Client ID of type **Web application**.
4. Add this **Authorized JavaScript origin**: `https://veer-barmeshwar-sena.onrender.com`
5. Add this **Authorized redirect URI** exactly: `https://veer-barmeshwar-sena.onrender.com/accounts/google/login/callback/`
6. Copy the generated client ID and client secret into Render Dashboard → your web service → Environment:
   - `GOOGLE_CLIENT_ID`
   - `GOOGLE_CLIENT_SECRET`
7. Save and redeploy. Visit `/accounts/login/` and test Google sign-in. For a custom domain, add that domain's HTTPS origin and callback URI in Google Cloud too.

Do not commit OAuth secrets to GitHub or send them in chat. Newly created Google accounts are regular members, not staff or superusers. Never let social login grant admin permissions.

## Video and media storage warning
The post editor accepts image and video uploads. Render's ordinary web-service filesystem is ephemeral; uploaded media can disappear after a redeploy or restart unless persistent storage is configured. Before publishing important videos, connect durable storage such as Cloudinary, Amazon S3, or a supported Render Persistent Disk and configure Django's media storage for it. Upload validation is a basic file-type/size check, not malware scanning or full file-signature validation.

## Tests and checks
```bash
python manage.py test
python manage.py check
python manage.py check --deploy
```

## Production checklist
- Set a strong `SECRET_KEY` in Render Environment.
- Keep `DEBUG=False`, HTTPS, correct hosts and trusted origins.
- Remove any temporary admin-bootstrap environment variables after initial admin setup.
- Configure SMTP if password reset emails are needed.
- Back up the production database and test restoration.
- Review community moderation and privacy practices before launch.

## Historical information
The About page provides brief, attributed historical context about Brahmeshwar Singh (“Brahmeshwar Mukhiya”), based on published reporting. The account is intentionally neutral and notes the violence and legal context rather than glorifying caste-based violence. The portrait is credited to the original news report; confirm permissions and usage rights before commercial reuse.

## Project layout
- `config/` settings and URLs
- `posts/` models, views, forms, admin, tests and migrations
- `templates/` server-rendered pages
- `static/` CSS and JavaScript
- `render.yaml` and `build.sh` deployment configuration
