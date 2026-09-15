from django.db import migrations, models
import django.db.models.deletion


def backfill_event_competition_and_phase(apps, schema_editor):
    Event = apps.get_model('events', 'Event')
    CompetitionStage = apps.get_model('events', 'CompetitionStage')
    for stage in CompetitionStage.objects.all():
        phase = 'FINAL' if (stage.stage_type or '').upper() == 'FINAL' else 'QUALIFIER'
        Event.objects.filter(competition_stage_id=stage.id).update(
            competition_id=stage.competition_id,
            phase=phase,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('competitions', '0004_competition_finalist_slots'),
        ('events', '0005_alter_enabledcompetitioncategory_unique_together_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='competition',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='events',
                to='competitions.competition',
            ),
        ),
        migrations.AddField(
            model_name='event',
            name='phase',
            field=models.CharField(
                choices=[('QUALIFIER', 'Qualifier'), ('FINAL', 'Final')],
                default='QUALIFIER',
                max_length=20,
            ),
        ),
        migrations.RunPython(backfill_event_competition_and_phase, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='event',
            name='competition',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='events',
                to='competitions.competition',
            ),
        ),
        migrations.RemoveConstraint(
            model_name='event',
            name='unique_event_number_per_stage',
        ),
        migrations.RemoveField(
            model_name='event',
            name='competition_stage',
        ),
        migrations.AddConstraint(
            model_name='event',
            constraint=models.UniqueConstraint(fields=('competition', 'phase', 'event_number'), name='unique_event_number_per_phase'),
        ),
        migrations.DeleteModel(
            name='CompetitionStage',
        ),
    ]


