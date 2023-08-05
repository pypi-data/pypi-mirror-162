from django.contrib import admin
from django import forms
from django.urls import path
from .models import Database, StateWatcher
from django_ace import AceWidget
from .methods import make_script
from . import views


class DatabaseForm(forms.ModelForm):
    class Meta:
        model = Database
        widgets = {
            'config': AceWidget(mode='json')
        }
        fields = ['handle', 'description', 'source', 'config']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # once an RDBMS type is selected, run the JS code to
        # show default JSON config for it
        self.fields['source'].widget.attrs.update(
            {"onchange": make_script('list_config')}
        )


class DatabaseAdmin(admin.ModelAdmin):
    form = DatabaseForm
    list_display = ['handle', 'description', 'source']

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('config', self.admin_site.admin_view(views.db_config))
        ]
        return custom_urls + urls


class StateWatcherForm(forms.ModelForm):
    class Meta:
        model = StateWatcher
        widgets = {
            'query': AceWidget(mode='sql')
        }
        fields = '__all__'


class StateWatcherAdmin(admin.ModelAdmin):
    form = StateWatcherForm
    list_display = ['database', 'name', 'target']


admin.site.register(Database, DatabaseAdmin)
admin.site.register(StateWatcher, StateWatcherAdmin)
