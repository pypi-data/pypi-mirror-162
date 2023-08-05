# Generated by Django 2.2.1 on 2019-05-05 07:59

from django.contrib.postgres.indexes import GinIndex
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tcms_github_marketplace", "0001_initial"),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name="purchase",
            name="tcms_github_marketplace_gin",
        ),
        migrations.RenameField(
            model_name="purchase",
            old_name="marketplace_purchase",
            new_name="payload",
        ),
        migrations.AddField(
            model_name="purchase",
            name="vendor",
            field=models.CharField(blank=True, db_index=True, max_length=16, null=True),
        ),
        migrations.AddIndex(
            model_name="purchase",
            index=GinIndex(
                fastupdate=False, fields=["payload"], name="tcms_github_payload_gin"
            ),
        ),
    ]
