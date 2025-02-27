# Generated by Django 2.2.17 on 2021-07-28 13:32

from django.db import migrations
import wagtail.core.blocks
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ("navigation", "0003_auto_20210415_1145"),
    ]

    operations = [
        migrations.AddField(
            model_name="navigationsettings",
            name="footer_top_links",
            field=wagtail.core.fields.StreamField(
                [
                    (
                        "link",
                        wagtail.core.blocks.StructBlock(
                            [
                                ("page", wagtail.core.blocks.PageChooserBlock()),
                                (
                                    "title",
                                    wagtail.core.blocks.CharBlock(
                                        help_text="Leave blank to use the page's own title",
                                        required=False,
                                    ),
                                ),
                            ]
                        ),
                    )
                ],
                blank=True,
                help_text="Single list of links that appear between the teasers and the addresses.",
            ),
        ),
    ]
