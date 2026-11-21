from django.contrib import admin
from .models import *
@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin): list_display=('code','title','category','full_marks','is_active'); search_fields=('code','title')
@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin): list_display=('subject','sequence','title'); list_filter=('subject',)
@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin): list_display=('unit','sequence','title'); list_filter=('unit__subject',)
for model in [SecuritySettings,Device,AppPreferences,Task,Reminder,Deck,Flashcard,FlashcardReview,StudySession,TopicProgress]:
    admin.site.register(model)
