# Veer Barmeshwar Sena — Django community platform

A Django server-rendered community publishing platform starter with a dark premium visual system, subtle CSS depth, admin publishing, public feed, likes, comments, reports, search, and Render deployment configuration.

## Important branding note
The GitHub repository supplied for this project was empty when inspected. The exact reference Facebook page could not be verified from the available link, so the interface uses configurable placeholder branding. Replace the initials, tagline, About copy, and artwork with assets/content approved by the organization before launch.

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
# Windows PowerShell: .venv\Scripts\Activate.ps1
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

## Create an administrator
```bash
python manage.py createsuperuser
```
The admin dashboard checks Django's `is_staff` flag. Never allow public registration to set staff/superuser status. Add a registration workflow only after defining email verification, rate limits, and account-abuse controls.

## Scheduled publication
A production scheduler is required; Render web services do not automatically run future `scheduled_at` posts. A production-safe approach is a scheduled Render job or Celery worker that runs a command which atomically publishes due posts. Implement and test that job before promising scheduled publishing to administrators.

## Render deployment
1. Push the project to your GitHub repository.
2. In Render, create a Blueprint and select this repository; review the PostgreSQL and web-service resources in `render.yaml`.
3. Set any additional environment variables, including `ALLOWED_HOSTS` if using a custom domain and `CSRF_TRUSTED_ORIGINS` with full HTTPS origins.
4. Ensure the build succeeds. The build script installs requirements, collects static files, and applies migrations.
5. Create the first superuser using the Render Shell: `python manage.py createsuperuser`.
6. Configure SMTP/email delivery for password resets.
7. Test all workflows and inspect logs before announcing the site.

## Security checklist before production
- Rotate/set a strong `SECRET_KEY` through Render environment variables.
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
