
from rest_framework import serializers


from .models import (
    Subject, Unit, Topic, Task, TaskCompletion, Reminder, Deck,
    Flashcard, FlashcardReview, StudySession, TopicProgress
)


class SubjectSerializer(serializers.ModelSerializer):
    unit_count = serializers.IntegerField(
        source='units.count',
        read_only=True,
    )

    class Meta:
        model = Subject
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class UnitSerializer(serializers.ModelSerializer):
    topic_count = serializers.IntegerField(
        source='topics.count',
        read_only=True,
    )

    class Meta:
        model = Unit
        fields = '__all__'


class TopicSerializer(serializers.ModelSerializer):
    subject_id = serializers.IntegerField(
        source='unit.subject_id',
        read_only=True,
    )
    subtopics = serializers.SerializerMethodField()

    class Meta:
        model = Topic
        fields = '__all__'

    def get_subtopics(self, obj):
        children = obj.subtopics.all().order_by('sequence')

        return TopicSerializer(
            children,
            many=True,
            context=self.context,
        ).data


class TaskSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(
        source='subject.title',
        read_only=True,
        allow_null=True,
    )
    topic_name = serializers.CharField(
        source='topic.title',
        read_only=True,
        allow_null=True,
    )
    unit_name = serializers.CharField(
        source='topic.unit.title',
        read_only=True,
        allow_null=True,
    )
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = (
            'created_at',
            'updated_at',
            'completed_at',
        )

    def get_is_overdue(self, obj):
        from django.utils import timezone

        return bool(
            obj.due_at
            and obj.due_at < timezone.now()
            and obj.status != 'done'
        )

    def update(self, instance, validated_data):
        from django.utils import timezone

        if (
            validated_data.get('status') == 'done'
            and instance.status != 'done'
        ):
            validated_data['completed_at'] = timezone.now()

        elif (
            validated_data.get('status')
            and validated_data['status'] != 'done'
        ):
            validated_data['completed_at'] = None

        return super().update(instance, validated_data)


class TaskCompletionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskCompletion
        fields = '__all__'
        read_only_fields = ('completed_at',)



class ReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reminder
        fields = '__all__'
        read_only_fields = ('created_at', 'delivered_at')


class DeckSerializer(serializers.ModelSerializer):
    card_count = serializers.SerializerMethodField()
    due_count = serializers.SerializerMethodField()

    class Meta:
        model = Deck
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

    def get_card_count(self, obj):
        return obj.cards.count()

    def get_due_count(self, obj):
        from django.utils import timezone

        return obj.cards.filter(
            due_at__lte=timezone.now()
        ).count()


class FlashcardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flashcard
        fields = '__all__'
        read_only_fields = (
            'interval_days',
            'ease_factor',
            'repetitions',
            'due_at',
            'last_reviewed_at',
            'created_at',
            'updated_at',
        )


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlashcardReview
        fields = '__all__'
        read_only_fields = (
            'previous_interval',
            'next_interval',
            'reviewed_at',
        )


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudySession
        fields = '__all__'
        read_only_fields = ('created_at',)

    def validate(self, attrs):
     start = attrs.get(
        'started_at',
        getattr(self.instance, 'started_at', None)
    )
     end = attrs.get(
        'ended_at',
        getattr(self.instance, 'ended_at', None)
    )

     if end and start and end < start:
        raise serializers.ValidationError(
            'ended_at cannot be before started_at'
        )

    # Respect the duration sent by the timer.
    # This is important because paused time must not count.
     if end and start and 'duration_minutes' not in attrs:
        attrs['duration_minutes'] = max(
            0,
            int((end - start).total_seconds() // 60)
        )

     return attrs

class TopicProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = TopicProgress
        fields = '__all__'
        read_only_fields = ('updated_at',)
