from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('api_tests', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='testresult',
            name='test_case',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='test_results', to='api_tests.TestCase'),
            preserve_default=False,
        ),
    ]
