from django.contrib import admin
from heura import models

class ContestAdmin(admin.ModelAdmin):
	list_display = [ 'id', 'type' ]
admin.site.register(models.Contest, ContestAdmin)

class InputAdmin(admin.ModelAdmin):
	list_display = [ 'id', 'contest' ]
admin.site.register(models.Input, InputAdmin)
