# Generated by Django 4.2.17 on 2025-01-25 06:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0004_alter_post_content'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='status',
            field=models.CharField(choices=[('대기', '대기'), ('처리 중', '처리 중'), ('처리 완료', '처리 완료')], default='대기', max_length=50),
        ),
    ]
