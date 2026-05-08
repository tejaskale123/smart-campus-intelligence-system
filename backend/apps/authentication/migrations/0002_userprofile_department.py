from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("authentication", "0001_userprofile"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="department",
            field=models.CharField(blank=True, default="", max_length=100),
        ),
    ]
