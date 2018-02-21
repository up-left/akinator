from django.contrib import admin

from . import models

admin.site.register(models.Game)
admin.site.register(models.Question)
admin.site.register(models.Guess)
admin.site.register(models.Answer)
admin.site.register(models.AnswerGuess)

