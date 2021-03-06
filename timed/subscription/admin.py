import hashlib

from django import forms
from django.contrib import admin

from . import models


@admin.register(models.Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Subscription admin view."""

    list_display = ['name', 'archived']


@admin.register(models.Package)
class PackageAdmin(admin.ModelAdmin):
    """Attendance admin view."""

    list_display = ['subscription', 'duration', 'price']


class SubscriptionProjectInline(admin.StackedInline):
    model = models.SubscriptionProject


class CustomerPasswordForm(forms.ModelForm):
    def save(self, commit=True):
        password = self.cleaned_data.get('password')
        if password is not None:
            self.instance.password = hashlib.md5(
                password.encode()).hexdigest()
        return super().save(commit=commit)


class CustomerPasswordInline(admin.StackedInline):
    form = CustomerPasswordForm
    model = models.CustomerPassword
