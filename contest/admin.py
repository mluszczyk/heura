from django.contrib import admin

from contest import models

class ContestAdmin(admin.ModelAdmin):
	list_display = [ 'id', 'type' ]
admin.site.register(models.Contest, ContestAdmin)

class TaskLongestCycle(admin.ModelAdmin):
	pass
admin.site.register(models.TaskLongestCycle, ContestAdmin)

class InputAdmin(admin.ModelAdmin):
	list_display = [ 'id', 'contest' ]
admin.site.register(models.Input, InputAdmin)
