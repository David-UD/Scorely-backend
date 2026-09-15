from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competitions', '0004_competition_finalist_slots'),
        ('events', '0007_enabledcompetitioncategory_finalist_slots'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='competition',
            name='finalist_slots',
        ),
    ]