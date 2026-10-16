# Veer Barmeshwar Sena — Django community platform

A Hindi-first, mobile-friendly community publishing platform for Veer Barmeshwar Sena, with a warm saffron/green visual palette, community imagery, admin publishing, public feed, likes, comments, reports, search, and Render deployment configuration.

## Branding note
The public interface now uses Hindi-first copy and a warm, familiar saffron/green palette. The homepage photo is loaded from Unsplash; replace it with an organization-approved local event/community photo when one is available. Confirm official contact details and organization copy before launch.

## Features included
- Public chronological feed with search and pagination.
- Only staff users can access the custom content dashboard and create/edit/delete posts.
- Django admin for user management and comment/report moderation.
- Draft, scheduled, published, and archived post states (scheduled publication needs the management command below).
- Image upload with size and declared MIME validation.
- Like/unlike with a database uniqueness constraint.
- Comments, replies model, author/admin comment deletion, and post reporting.
- Password login and password-reset view (configure production email).
- Audit records for admin post changes.
- Render Blueprint with PostgreSQL, WhiteNoise, build script, Gunicorn.
- Automated baseline tests.

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

The settings module reads environment variables directly. Set `SECRET_KEY` and `DEBUG=True` for local development. Do not use the development key in production.

## Tests and checks
```bash
python manage.py test
python manage.py check
python manage.py check --deploy
```
Tests should be run in the target environment before launch. This project archive has not been deployed and no test result should be assumed until those commands pass.

## Create the production administrator without Render Shell
The public navigation intentionally has no admin-login button. Use Django's built-in admin at `/admin/`; do not add a public admin-registration page.

For a first-time setup when Render Shell is unavailable:

1. Open the Render Dashboard and select this web service.
2. Open **Environment** and temporarily add these variables. Use your own values; do not put the password in GitHub or share it in chat.
   - `DJANGO_ADMIN_USERNAME`: a new admin username that does not already exist.
   - `DJANGO_ADMIN_PASSWORD`: a strong, unique password (at least 15 characters recommended).
   - `DJANGO_ADMIN_EMAIL`: your admin email address (optional).
3. Save changes and trigger a deploy if Render does not start one automatically. The build script runs migrations, then creates the superuser only if that username is not already present.
4. Wait for the deployment to finish successfully, then sign in at `https://veer-barmeshwar-sena.onrender.com/admin/` with the username and password you configured.
5. After the first successful login, return to Render **Environment** and delete all three `DJANGO_ADMIN_*` variables, then save. This prevents credentials from remaining in the service environment. Do not delete `SECRET_KEY` or `DATABASE_URL`.
6. If the username already exists, this bootstrap deliberately does not change its password or permissions. Choose a different username for first-time setup. For an existing account whose password is forgotten, use an authorized database/admin recovery method rather than making a public password-reset endpoint.

If the build fails, check Render's deploy logs. Do not keep retrying with a password that has been exposed; rotate it in Render Environment.

Never allow public registration to set staff/superuser status.

## Render deployment
1. Push the project to GitHub and connect the repository to Render.
2. Review the PostgreSQL and web-service resources in `render.yaml`.
3. Set any additional environment variables, including `ALLOWED_HOSTS` if using a custom domain and `CSRF_TRUSTED_ORIGINS` with full HTTPS origins.
4. Ensure the build succeeds. The build script installs requirements, collects static files, applies migrations, and optionally creates the initial admin if the temporary `DJANGO_ADMIN_*` variables are present.
5. Configure SMTP/email delivery for password resets.
6. Test all workflows and inspect logs before announcing the site.

## Security checklist before production
- Rotate/set a strong `SECRET_KEY` through Render environment variables.
- Remove the temporary `DJANGO_ADMIN_*` variables immediately after the first successful admin login.
- Set correct `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, HTTPS, and HSTS only after HTTPS is verified.
- Configure SMTP and generic password-reset behavior.
- Add request rate limiting (for example, a trusted proxy-aware middleware or platform/WAF control) for login, comments, and reports.
- Review upload security: content-type checking here is a baseline, not full file-signature validation or malware scanning. Add signature inspection/re-encoding and storage isolation before accepting public uploads.
- Add email verification, account registration, profile settings, notification preferences, and account deletion only with a documented privacy policy.
- Review policy pages with the organization and applicable legal requirements.
- Add an explicit reply form if public threaded replies are required; the model supports parent comments, but this starter does not yet expose a reply-posting workflow.
- Add moderation/report handling screens and audit-log access controls.
- Configure backups and test restoring the production database.
- Run dependency auditing, `manage.py check --deploy`, and the full test suite before public launch.

## Project layout
- `config/` settings and WSGI/ASGI
- `posts/` posts, interactions, moderation models, views, admin, tests
- `templates/` server-rendered pages
- `static/` CSS and JavaScript
- `render.yaml` and `build.sh` deployment configuration
