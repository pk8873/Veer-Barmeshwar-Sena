from django.conf import settings
from django.db import migrations


def create_profiles_for_existing_users(apps, schema_editor):
    MemberProfile = apps.get_model("posts", "MemberProfile")
    app_label, model_name = settings.AUTH_USER_MODEL.split(".")
    User = apps.get_model(app_label, model_name)
    database = schema_editor.connection.alias
    existing_ids = MemberProfile.objects.using(database).values_list("user_id", flat=True)
    MemberProfile.objects.using(database).bulk_create(
        [
            MemberProfile(user_id=user_id)
            for user_id in User.objects.using(database).exclude(pk__in=existing_ids).values_list("pk", flat=True)
        ],
        ignore_conflicts=True,
    )


class Migration(migrations.Migration):
    dependencies = [
        ("posts", "0003_memberprofile"),
    ]

    operations = [
        migrations.RunPython(create_profiles_for_existing_users, migrations.RunPython.noop),
    ]
