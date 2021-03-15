# Generated by Django 2.2.17 on 2021-03-12 11:50

from django.db import migrations
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ("people", "0020_culturepagekeypoint"),
    ]

    operations = [
        migrations.RenameField(
            model_name="culturepage",
            old_name="heading_for_key_points",
            new_name="benefits_heading",
        ),
        migrations.RenameField(
            model_name="culturepage",
            old_name="key_points_section_title",
            new_name="benefits_section_title",
        ),
        migrations.AlterField(
            model_name="culturepagekeypoint",
            name="page",
            field=modelcluster.fields.ParentalKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="key_benefits",
                to="people.CulturePage",
            ),
        ),
    ]
