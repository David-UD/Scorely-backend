from django.db import migrations, models


def backfill_finalist_slots(apps, schema_editor):
    EnabledCompetitionCategory = apps.get_model('events', 'EnabledCompetitionCategory')
    for enabled_category in EnabledCompetitionCategory.objects.select_related('competition'):
        enabled_category.finalist_slots = enabled_category.competition.finalist_slots
        enabled_category.save(update_fields=['finalist_slots'])


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0006_remove_competitionstage_competition_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='enabledcompetitioncategory',
            name='finalist_slots',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.RunPython(backfill_finalist_slots, migrations.RunPython.noop),
    ]