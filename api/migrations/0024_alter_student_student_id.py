# Generated by Django 4.2.2 on 2023-06-22 17:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0023_alter_student_amount_elective_alter_student_courses'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='student_id',
            field=models.IntegerField(null=True),
        ),
    ]
