# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('slug', models.SlugField()),
                ('help_text', models.TextField(null=True, blank=True)),
                ('score', models.IntegerField(default=0)),
                ('order', models.IntegerField(default=0)),
                ('is_default', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ('question', 'order', 'slug'),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GroupedAnswer',
            fields=[
                ('answer_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='web.Answer')),
                ('group', models.CharField(max_length=255)),
            ],
            options={
                'ordering': ('group', 'order', 'slug'),
            },
            bases=('web.answer',),
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(help_text=b'A slug for identifying answers to this specific question (allows multiple only for multiple languages)')),
                ('label', models.CharField(max_length=512, blank=True)),
                ('help_text', models.CharField(max_length=512, blank=True)),
                ('question_type', models.CharField(max_length=1, choices=[(b'S', b'Single-choice question'), (b'M', b'Multi-choice question'), (b'F', b'Free-text question'), (b'P', b'Prioritise question')])),
                ('optional', models.BooleanField(default=False, help_text=b'Only applies to free text questions')),
                ('depends_on_answer', models.ForeignKey(related_name='trigger_questions', blank=True, to='web.Answer', null=True)),
                ('tags', taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', blank=True, help_text='A comma-separated list of tags.', verbose_name='Tags')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('question', models.SlugField()),
                ('answer', models.TextField(blank=True)),
                ('score', models.IntegerField()),
            ],
            options={
                'ordering': ('submission_set', 'user', 'question'),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SubmissionSet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(blank=True)),
                ('tag', models.SlugField(blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(related_name='saq_submissions_sets', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='submission',
            name='submission_set',
            field=models.ForeignKey(related_name='submissions', to='web.SubmissionSet', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='submission',
            name='user',
            field=models.ForeignKey(related_name='saq_submissions', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='submission',
            unique_together=set([('question', 'user', 'submission_set')]),
        ),
        migrations.AddField(
            model_name='answer',
            name='question',
            field=models.ForeignKey(related_name='answers', to='web.Question'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='answer',
            unique_together=set([('question', 'slug')]),
        ),
    ]
