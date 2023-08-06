from django.contrib import admin
from .models import Action, States, TransitionManager
# Register your models here.
from django.conf import settings




admin.site.register(TransitionManager)
admin.site.register(Action )
admin.site.register(States)