# Generated by Django 2.2.17 on 2021-11-12 14:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("people", "0029_auto_20210728_1109"),
    ]

    operations = [
        migrations.AlterField(
            model_name="author",
            name="image",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="images.CustomImage",
            ),
        ),
        migrations.AlterField(
            model_name="contact",
            name="image",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="images.CustomImage",
            ),
        ),
        migrations.AlterField(
            model_name="culturepage",
            name="hero_image",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="images.CustomImage",
            ),
        ),
        migrations.AlterField(
            model_name="personpage",
            name="image",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="images.CustomImage",
            ),
        ),
        migrations.AlterField(
            model_name="valuespagevalue",
            name="value_image",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="images.CustomImage",
            ),
        ),
    ]
