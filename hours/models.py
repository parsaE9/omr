# coding: utf-8

from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
import moratab, jdatetime

light_colors = [('#ff9896', 'Red'), ('#f7b6d2', 'Pink'), ('#c5b0d5', 'Purple'), ('#68d8fd', 'Blue'),
                ('#9edae5', 'Cyan'), ('#98df8a', 'Green'), ('#dbdb8d', 'Olive'), ('#f5ff66', 'Yellow'),
                ('#c49c94', 'Brown'), ('#ffbb78', 'Orange')]
jalali_date = lambda date: jdatetime.date.fromgregorian(date=date, locale='fa_IR')


def time_format(duration):
    minutes, _ = divmod(duration.days * 24 * 60 * 60 + duration.seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return '{}:{:0>2}'.format(hours, minutes)


class Organization(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    admin = models.ForeignKey(User, related_name='owned_organizations', on_delete=models.CASCADE)
    employees = models.ManyToManyField(User)
    invitations = models.TextField(blank=True)

    def projects(self):
        return self.project_set.filter(active=True).order_by('id')

    def ordered_employees(self):
        return self.employees.order_by('last_name')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return '/%s' % self.slug


class Project(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    color = models.CharField(max_length=10, choices=light_colors)
    active = models.BooleanField(default=True)

    def save(self, **kwargs):
        if not self.color:
            self.color = light_colors[self.organization.project_set.count() % len(light_colors)]
        super(Project, self).save()

    def __str__(self):
        return self.title


class Work(models.Model):
    employee = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    duration = models.DurationField()
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, blank=True, null=True, on_delete=models.CASCADE)
    description = models.CharField(max_length=255, blank=True, null=True)

    def date_text(self):
        return jalali_date(self.date).strftime('%A، %-d %B %Y')

    def date_number(self):
        return jalali_date(self.date).strftime('%Y/%m/%d')

    def duration_text(self):
        return time_format(self.duration)

    def __str__(self):
        return '{} - {} - {} - {}'.format(self.organization.title, self.employee.last_name, self.date, self.duration)

    def get_absolute_url(self):
        return self.organization.get_absolute_url()


class Note(models.Model):
    employee = models.ForeignKey(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    content = models.CharField(max_length=255)
    content_html = models.CharField(max_length=255, blank=True)
    category = models.CharField(max_length=20,
                                choices=(('success', 'سبز'), ('info', 'آبی'), ('warning', 'زرد'), ('danger', 'قرمز')))
    date = models.DateField()

    def clean(self):
        self.content_html = moratab.render(self.content)

    def date_number(self):
        return jalali_date(self.date).strftime('%Y/%m/%d')

    def date_text(self):
        jdatetime.set_locale('Persian_Iran')
        return jalali_date(self.date).strftime('%A، %-d %B %Y')

    def __str__(self):
        return '{} - {} - {}'.format(self.organization.title, self.employee.last_name, self.content)

    def get_absolute_url(self):
        return reverse('employee-notes', args=[self.organization.slug])


class Holiday(models.Model):
    class Meta:
        ordering = ['-date']

    date = models.DateField(unique=True, null=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    is_weekend = models.BooleanField(default=False)

    def __str__(self):
        if self.description:
            return str(self.date) + ' : ' + self.description
        else:
            return str(self.date)

    def date_text(self):
        return jalali_date(self.date).strftime('%A، %-d %B %Y')

    def date_number(self):
        return jalali_date(self.date).strftime('%Y/%m/%d')