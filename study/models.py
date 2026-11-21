import uuid
from django.db import models
from django.utils import timezone

class SecuritySettings(models.Model):
    pin_hash = models.CharField(max_length=256)
    recovery_hash = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Device(models.Model):
    device_id = models.CharField(max_length=128, unique=True)
    label = models.CharField(max_length=120, default='My Android phone')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(null=True, blank=True)


class AppPreferences(models.Model):
    lock_timeout_minutes = models.PositiveSmallIntegerField(default=5)
    daily_goal_minutes = models.PositiveSmallIntegerField(default=120)
    notifications_enabled = models.BooleanField(default=True)
    reminder_advance_minutes = models.PositiveSmallIntegerField(default=10)
    updated_at = models.DateTimeField(auto_now=True)

class SyncModel(models.Model):
    """Versioned client-owned JSON record for offline-first synchronization."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entity_type = models.CharField(max_length=60, db_index=True)
    entity_id = models.UUIDField(db_index=True)
    payload = models.JSONField(default=dict)
    revision = models.PositiveIntegerField(default=1)
    deleted_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['entity_type','entity_id'], name='unique_sync_entity')]
        ordering = ['updated_at']

class SyncConflict(models.Model):
    entity_type = models.CharField(max_length=60)
    entity_id = models.UUIDField()
    server_revision = models.PositiveIntegerField()
    client_base_revision = models.PositiveIntegerField()
    server_payload = models.JSONField(default=dict)
    client_payload = models.JSONField(default=dict)
    resolved = models.BooleanField(default=False)
    resolution = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

class Subject(models.Model):
    class Category(models.TextChoices): CORE='core','Core'; COMPULSORY='compulsory','Compulsory'; ELECTIVE='elective','Elective'
    code = models.CharField(max_length=30, unique=True)
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=Category.choices)
    full_marks = models.PositiveSmallIntegerField(null=True, blank=True)
    pass_marks = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    lecture_hours = models.PositiveSmallIntegerField(null=True, blank=True)
    year = models.PositiveSmallIntegerField(default=3)
    is_active = models.BooleanField(default=True)
    syllabus_source = models.URLField(blank=True)
    syllabus_version = models.CharField(max_length=80, blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta: ordering=['sort_order','code']
    def __str__(self): return f'{self.code} - {self.title}'

class Unit(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='units')
    code = models.CharField(max_length=30, blank=True)
    title = models.CharField(max_length=240)
    description = models.TextField(blank=True)
    sequence = models.PositiveSmallIntegerField(default=1)
    lecture_hours = models.PositiveSmallIntegerField(null=True, blank=True)
    is_custom = models.BooleanField(default=False)
    class Meta: ordering=['sequence']; unique_together=[('subject','sequence')]

class Topic(models.Model):
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='topics')
    title = models.CharField(max_length=1000)
    description = models.TextField(blank=True)
    sequence = models.PositiveSmallIntegerField(default=1)
    estimated_minutes = models.PositiveSmallIntegerField(default=30)
    is_custom = models.BooleanField(default=False)
    class Meta: ordering=['sequence']; unique_together=[('unit','sequence')]
    parent = models.ForeignKey(
    'self',
    on_delete=models.CASCADE,
    null=True,
    blank=True,
    related_name='subtopics',
)

class Material(models.Model):
    class Kind(models.TextChoices): PDF='pdf','PDF'; IMAGE='image','Image'; NOTE='note','Note'; OTHER='other','Other'
    title = models.CharField(max_length=240)
    kind = models.CharField(max_length=10, choices=Kind.choices, default=Kind.NOTE)
    subject = models.ForeignKey(Subject, null=True, blank=True, on_delete=models.SET_NULL, related_name='materials')
    unit = models.ForeignKey(Unit, null=True, blank=True, on_delete=models.SET_NULL, related_name='materials')
    topic = models.ForeignKey(Topic, null=True, blank=True, on_delete=models.SET_NULL, related_name='materials')
    description = models.TextField(blank=True)
    note_body = models.TextField(blank=True)
    storage_path = models.CharField(max_length=500, blank=True)
    original_filename = models.CharField(max_length=255, blank=True)
    mime_type = models.CharField(max_length=120, blank=True)
    size_bytes = models.PositiveBigIntegerField(default=0)
    is_bookmarked = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    last_revised_at = models.DateTimeField(null=True, blank=True)
    revision_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta: ordering=['-updated_at']

class Annotation(models.Model):
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='annotations')
    title = models.CharField(max_length=160, blank=True)
    body = models.TextField()
    page_number = models.PositiveIntegerField(null=True, blank=True)
    anchor = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Task(models.Model):
    class Status(models.TextChoices): TODO='todo','To do'; IN_PROGRESS='in_progress','In progress'; DONE='done','Done'
    title = models.CharField(max_length=240)
    description = models.TextField(blank=True)
    subject = models.ForeignKey(Subject, null=True, blank=True, on_delete=models.SET_NULL, related_name='tasks')
    topic = models.ForeignKey(Topic, null=True, blank=True, on_delete=models.SET_NULL, related_name='tasks')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.TODO)
    priority = models.CharField(max_length=10, choices=[('low','Low'),('medium','Medium'),('high','High')], default='medium')
    due_at = models.DateTimeField(null=True, blank=True)
    start_at = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.PositiveSmallIntegerField(default=30)
    recurrence_rule = models.CharField(max_length=300, blank=True, help_text='RFC 5545 RRULE; interpreted by the mobile planner')
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta: ordering=['due_at','-created_at']


class TaskCompletion(models.Model):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='daily_completions',
    )
    date = models.DateField()
    completed_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-date']
        constraints = [
            models.UniqueConstraint(
                fields=['task', 'date'],
                name='unique_task_completion_per_day',
            ),
        ]

    def __str__(self):
        return f'{self.task.title} - {self.date}'


class Reminder(models.Model):
    task = models.ForeignKey(Task, null=True, blank=True, on_delete=models.CASCADE, related_name='reminders')
    title = models.CharField(max_length=200)
    message = models.CharField(max_length=500, blank=True)
    scheduled_at = models.DateTimeField()
    channel = models.CharField(max_length=20, choices=[('both','Both'),('in_app','In app'),('push','Phone notification')], default='both')
    is_enabled = models.BooleanField(default=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Deck(models.Model):
    subject = models.ForeignKey(Subject, null=True, blank=True, on_delete=models.SET_NULL, related_name='decks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Flashcard(models.Model):
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE, related_name='cards')
    title = models.CharField(max_length=200, blank=True)
    front = models.TextField()
    back = models.TextField()
    hint = models.TextField(blank=True)
    difficulty = models.CharField(max_length=12, choices=[('easy','Easy'),('medium','Medium'),('hard','Hard')], default='medium')
    interval_days = models.PositiveIntegerField(default=0)
    ease_factor = models.DecimalField(max_digits=4, decimal_places=2, default=2.50)
    repetitions = models.PositiveIntegerField(default=0)
    due_at = models.DateTimeField(default=timezone.now, db_index=True)
    last_reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta: ordering=['due_at','id']

class FlashcardReview(models.Model):
    card = models.ForeignKey(Flashcard, on_delete=models.CASCADE, related_name='reviews')
    rating = models.CharField(max_length=12, choices=[('again','Again'),('hard','Hard'),('good','Good'),('easy','Easy')])
    previous_interval = models.PositiveIntegerField(default=0)
    next_interval = models.PositiveIntegerField(default=0)
    reviewed_at = models.DateTimeField(auto_now_add=True)

class StudySession(models.Model):
    subject = models.ForeignKey(Subject, null=True, blank=True, on_delete=models.SET_NULL, related_name='sessions')
    topic = models.ForeignKey(Topic, null=True, blank=True, on_delete=models.SET_NULL, related_name='sessions')
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(default=0)
    note = models.TextField(blank=True)
    source = models.CharField(max_length=20, choices=[('timer','Timer'),('manual','Manual')], default='timer')
    created_at = models.DateTimeField(auto_now_add=True)

class TopicProgress(models.Model):
    topic = models.OneToOneField(Topic, on_delete=models.CASCADE, related_name='progress')
    status = models.CharField(max_length=16, choices=[('not_started','Not started'),('learning','Learning'),('revising','Revising'),('mastered','Mastered')], default='not_started')
    completion_percent = models.PositiveSmallIntegerField(default=0)
    confidence = models.PositiveSmallIntegerField(default=0)
    last_studied_at = models.DateTimeField(null=True, blank=True)
    revision_count = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)
    def save(self,*args,**kwargs):
        self.completion_percent = min(100,max(0,self.completion_percent))
        self.confidence = min(5,max(0,self.confidence))
        super().save(*args,**kwargs)
