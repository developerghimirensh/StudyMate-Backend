import json
import secrets
import uuid

from datetime import timedelta

from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.db import transaction
from django.db.models import Sum, Count, Avg
from django.http import HttpResponse
from django.utils import timezone, dateparse

from rest_framework import viewsets, status
from rest_framework.decorators import (
    action,
    api_view,
    permission_classes,
    throttle_classes,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.throttling import AnonRateThrottle

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from .models import *
from .serializers import *


class SecurityThrottle(AnonRateThrottle):
    scope = 'security'


def issue_tokens(device_id):
    from django.contrib.auth import get_user_model

    User = get_user_model()

    user, _ = User.objects.get_or_create(
        username='studymate-local-owner',
        defaults={'is_active': True},
    )

    refresh = RefreshToken.for_user(user)
    refresh['device_id'] = device_id

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'token_type': 'Bearer',
    }


def get_security():
    return SecuritySettings.objects.order_by('id').first()


class SecuritySetupView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [SecurityThrottle]

    def post(self, request):
        pin = str(request.data.get('pin', ''))
        device_id = str(
            request.data.get('device_id', '')
        ).strip()
        label = str(
            request.data.get('device_label', 'My Android phone')
        )[:120]

        if (
            not settings.SETUP_SECRET
            or not secrets.compare_digest(
                str(request.data.get('setup_secret', '')),
                settings.SETUP_SECRET,
            )
        ):
            return Response(
                {'detail': 'Invalid setup authorization.'},
                status=403,
            )

        if len(pin) != 6 or not pin.isdigit():
            return Response(
                {'detail': 'PIN must contain exactly six digits.'},
                status=400,
            )

        if not device_id or len(device_id) > 128:
            return Response(
                {'detail': 'A stable device_id is required.'},
                status=400,
            )

        with transaction.atomic():
            if get_security():
                return Response(
                    {'detail': 'StudyMate security is already configured.'},
                    status=409,
                )

            recovery = secrets.token_urlsafe(24)

            SecuritySettings.objects.create(
                pin_hash=make_password(pin),
                recovery_hash=make_password(recovery),
            )

            Device.objects.update_or_create(
                device_id=device_id,
                defaults={
                    'label': label,
                    'is_active': True,
                    'last_seen': timezone.now(),
                },
            )

        return Response(
            {
                'message': (
                    'Security configured. Save this recovery key now; '
                    'it will not be shown again.'
                ),
                'recovery_key': recovery,
                **issue_tokens(device_id),
            },
            status=201,
        )


class SecurityUnlockView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [SecurityThrottle]

    def post(self, request):
        sec = get_security()
        pin = str(request.data.get('pin', ''))
        device_id = str(
            request.data.get('device_id', '')
        ).strip()

        if not sec:
            return Response(
                {'detail': 'Complete initial setup first.'},
                status=409,
            )

        if not check_password(pin, sec.pin_hash):
            return Response(
                {'detail': 'Incorrect PIN.'},
                status=401,
            )

        device = Device.objects.filter(
            device_id=device_id,
            is_active=True,
        ).first()

        if not device:
            return Response(
                {
                    'detail': (
                        'This device is not authorized. '
                        'Re-authorize it using the recovery key.'
                    )
                },
                status=403,
            )

        device.last_seen = timezone.now()
        device.save(update_fields=['last_seen'])

        return Response(issue_tokens(device_id))


class SecurityRecoverView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [SecurityThrottle]

    def post(self, request):
        sec = get_security()
        key = str(request.data.get('recovery_key', ''))
        pin = str(request.data.get('new_pin', ''))

        if not sec:
            return Response(
                {'detail': 'Security is not configured.'},
                status=404,
            )

        if not check_password(key, sec.recovery_hash):
            return Response(
                {'detail': 'Invalid recovery key.'},
                status=401,
            )

        if len(pin) != 6 or not pin.isdigit():
            return Response(
                {'detail': 'New PIN must contain exactly six digits.'},
                status=400,
            )

        new_recovery = secrets.token_urlsafe(24)

        sec.pin_hash = make_password(pin)
        sec.recovery_hash = make_password(new_recovery)
        sec.save()

        return Response(
            {
                'message': (
                    'PIN reset. Save the new recovery key now; '
                    'it will not be shown again.'
                ),
                'recovery_key': new_recovery,
            }
        )


class ChangePinView(APIView):
    def post(self, request):
        sec = get_security()
        old = str(request.data.get('current_pin', ''))
        new = str(request.data.get('new_pin', ''))

        if not sec or not check_password(old, sec.pin_hash):
            return Response(
                {'detail': 'Current PIN is incorrect.'},
                status=400,
            )

        if len(new) != 6 or not new.isdigit():
            return Response(
                {'detail': 'New PIN must contain exactly six digits.'},
                status=400,
            )

        sec.pin_hash = make_password(new)
        sec.save(update_fields=['pin_hash', 'updated_at'])

        return Response({'message': 'PIN changed successfully.'})


@api_view(['GET'])
@permission_classes([AllowAny])
def health(request):
    return Response({
        'status': 'ok',
        'service': 'StudyMate API',
        'time': timezone.now(),
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def security_status(request):
    configured = bool(get_security())

    return Response({
        'is_configured': configured,
        'setup_required': not configured,
    })


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.filter(is_active=True)
    serializer_class = SubjectSerializer
    search_fields = ['code', 'title']
    ordering_fields = ['sort_order', 'code', 'title']

    @action(detail=True, methods=['get'])
    def outline(self, request, pk=None):
        subject = self.get_object()
        units = []

        for unit in subject.units.all().order_by('sequence'):
            top_level_topics = (
                unit.topics
                .filter(parent__isnull=True)
                .order_by('sequence')
            )

            units.append({
                'id': unit.id,
                'subject': unit.subject_id,
                'code': unit.code,
                'title': unit.title,
                'description': unit.description,
                'sequence': unit.sequence,
                'lecture_hours': unit.lecture_hours,
                'is_custom': unit.is_custom,
                'topics': TopicSerializer(
                    top_level_topics,
                    many=True,
                    context=self.get_serializer_context(),
                ).data,
            })

        return Response({
            'subject': SubjectSerializer(
                subject,
                context=self.get_serializer_context(),
            ).data,
            'units': units,
        })


class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.select_related('subject').all()
    serializer_class = UnitSerializer
    filterset_fields = ['subject']
    search_fields = ['title', 'code']


class TopicViewSet(viewsets.ModelViewSet):
    queryset = (
        Topic.objects
        .select_related('unit', 'unit__subject', 'parent')
        .prefetch_related('subtopics')
        .all()
    )

    serializer_class = TopicSerializer

    filterset_fields = [
        'unit',
        'unit__subject',
        'parent',
    ]

    search_fields = ['title', 'description']


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.select_related(
        'subject',
        'topic',
    ).all()

    serializer_class = TaskSerializer
    pagination_class = None

    filterset_fields = [
        'status',
        'priority',
        'subject',
        'topic',
    ]

    search_fields = ['title', 'description']

    ordering_fields = [
        'due_at',
        'created_at',
        'priority',
    ]

    @action(
        detail=False,
        methods=['get'],
        url_path='completions',
    )
    def completions(self, request):
        start = dateparse.parse_date(
            request.query_params.get('start', '')
        )
        end = dateparse.parse_date(
            request.query_params.get('end', '')
        )

        if not start or not end:
            return Response(
                {'detail': 'Both start and end dates are required (YYYY-MM-DD).'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if end < start:
            return Response(
                {'detail': 'End date cannot be before start date.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        records = TaskCompletion.objects.filter(
            task__in=self.get_queryset(),
            date__range=(start, end),
        ).select_related('task')

        return Response(
            TaskCompletionSerializer(records, many=True).data
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='completion',
    )
    def completion(self, request, pk=None):
        task = self.get_object()

        completion_date = dateparse.parse_date(
            request.data.get('date', '')
        )

        if not completion_date:
            return Response(
                {'detail': 'A valid date in YYYY-MM-DD format is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.method == 'POST':
            record, created = TaskCompletion.objects.get_or_create(
                task=task,
                date=completion_date,
            )

            return Response(
                TaskCompletionSerializer(record).data,
                status=(
                    status.HTTP_201_CREATED
                    if created
                    else status.HTTP_200_OK
                ),
            )

        deleted_count, _ = TaskCompletion.objects.filter(
            task=task,
            date=completion_date,
        ).delete()

        return Response(
            {'completed': False, 'deleted': bool(deleted_count)},
            status=status.HTTP_200_OK,
        )


class ReminderViewSet(viewsets.ModelViewSet):
    queryset = Reminder.objects.select_related('task').all()
    serializer_class = ReminderSerializer

    filterset_fields = [
        'task',
        'channel',
        'is_enabled',
    ]

    ordering_fields = ['scheduled_at']


class DeckViewSet(viewsets.ModelViewSet):
    queryset = (
        Deck.objects
        .select_related('subject')
        .prefetch_related('cards')
        .all()
    )

    serializer_class = DeckSerializer
    filterset_fields = ['subject']
    search_fields = ['title', 'description']


class FlashcardViewSet(viewsets.ModelViewSet):
    queryset = (
        Flashcard.objects
        .select_related('deck', 'deck__subject')
        .all()
    )

    serializer_class = FlashcardSerializer
    pagination_class = None

    filterset_fields = ['deck', 'difficulty']

    search_fields = ['front', 'back']

    ordering_fields = ['due_at', 'created_at']

    @action(detail=False, methods=['get'])
    def due(self, request):
        cards = self.get_queryset().filter(
            due_at__lte=timezone.now()
        )

        if request.query_params.get('deck'):
            cards = cards.filter(
                deck_id=request.query_params['deck']
            )

        return Response(self.get_serializer(cards, many=True).data)


class ReviewViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FlashcardReview.objects.select_related('card').all()
    serializer_class = ReviewSerializer
    filterset_fields = ['card', 'rating']

    @action(detail=False, methods=['post'], url_path='submit')
    def submit(self, request):
        card_id = request.data.get('card')
        rating = request.data.get('rating')

        if rating not in ('again', 'hard', 'good', 'easy'):
            return Response(
                {'detail': 'rating must be again, hard, good, or easy.'},
                status=400,
            )

        card = Flashcard.objects.filter(pk=card_id).first()

        if not card:
            return Response(
                {'detail': 'Flashcard not found.'},
                status=404,
            )

        old = card.interval_days
        ef = float(card.ease_factor)

        if rating == 'again':
            card.repetitions = 0
            interval = 1
            ef = max(1.3, ef - 0.2)

        elif rating == 'hard':
            card.repetitions += 1
            interval = max(1, round(max(1, old) * 1.2))
            ef = max(1.3, ef - 0.15)

        elif rating == 'good':
            card.repetitions += 1
            interval = (
                1 if old == 0
                else (
                    6 if card.repetitions == 2
                    else max(1, round(old * ef))
                )
            )

        else:
            card.repetitions += 1
            interval = (
                4 if old == 0
                else max(2, round(max(1, old) * ef * 1.3))
            )
            ef += 0.15

        card.interval_days = interval
        card.ease_factor = round(ef, 2)
        card.due_at = timezone.now() + timedelta(days=interval)
        card.last_reviewed_at = timezone.now()
        card.save()

        review = FlashcardReview.objects.create(
            card=card,
            rating=rating,
            previous_interval=old,
            next_interval=interval,
        )

        return Response(
            {
                'review': ReviewSerializer(review).data,
                'card': FlashcardSerializer(card).data,
            },
            status=201,
        )


class StudySessionViewSet(viewsets.ModelViewSet):
    queryset = StudySession.objects.select_related(
        'subject',
        'topic',
    ).all()

    serializer_class = SessionSerializer

    filterset_fields = [
        'subject',
        'topic',
        'source',
    ]

    ordering_fields = [
        'started_at',
        'duration_minutes',
    ]


class TopicProgressViewSet(viewsets.ModelViewSet):
    queryset = TopicProgress.objects.select_related(
        'topic',
        'topic__unit',
    ).all()

    serializer_class = TopicProgressSerializer
    filterset_fields = ['status']
    search_fields = ['topic__title']


# ------------------------------------------------------
# DASHBOARD
# ------------------------------------------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard(request):
    today = timezone.localdate()
    week_start = today - timedelta(days=today.weekday())
    completed_sessions = StudySession.objects.filter(
    ended_at__isnull=False,
     ).count()

    # --------------------------------------------------
    # WEEKLY STUDY TIME
    # --------------------------------------------------

    weekly_study_minutes = (
        StudySession.objects.filter(
            started_at__date__gte=week_start,
            started_at__date__lte=today,
            ended_at__isnull=False,
        ).aggregate(
            total=Sum('duration_minutes')
        )['total'] or 0
    )

    weekly_sessions = StudySession.objects.filter(
    started_at__date__gte=week_start,
    started_at__date__lte=today,
    ended_at__isnull=False,
)

    weekly_study_minutes = (
    weekly_sessions.aggregate(
        total=Sum('duration_minutes')
    )['total'] or 0
)

    weekly_study_minutes = int(weekly_study_minutes)

    weekly_study_hours = round(
        weekly_study_minutes / 60,
        1,
    )

    # --------------------------------------------------
    # TASK STATISTICS
    # --------------------------------------------------

    completed_tasks = Task.objects.filter(
        status='done'
    ).count()

    pending_tasks = Task.objects.exclude(
        status='done'
    ).count()

    # --------------------------------------------------
    # FLASHCARDS DUE
    # --------------------------------------------------

    flashcards_due = Flashcard.objects.filter(
        due_at__lte=timezone.now()
    ).count()

    # --------------------------------------------------
    # SYLLABUS TOPICS
    # Only leaf topics are counted.
    # --------------------------------------------------

    topics = Topic.objects.filter(
        unit__subject__is_active=True,
        subtopics__isnull=True,
    ).select_related(
        'unit',
        'unit__subject',
    )

    topic_ids = list(
        topics.values_list('id', flat=True)
    )

    # --------------------------------------------------
    # TOPIC PROGRESS
    # Fetch completion percentage AND status together.
    # --------------------------------------------------

    progress_records = TopicProgress.objects.filter(
        topic_id__in=topic_ids
    ).values_list(
        'topic_id',
        'completion_percent',
        'status',
    )

    progress_by_topic = {}
    status_by_topic = {}

    for topic_id, percent, progress_status in progress_records:
        progress_by_topic[topic_id] = float(
            percent or 0
        )

        status_by_topic[topic_id] = progress_status

    # --------------------------------------------------
    # PLANNER COMPLETIONS
    # Completed planner tasks contribute to topic progress.
    # Each TaskCompletion record is counted separately.
    # --------------------------------------------------

    planner_minutes_by_topic = {}

    planner_data = (
        TaskCompletion.objects.filter(
            task__topic_id__in=topic_ids
        )
        .values('task__topic_id')
        .annotate(
            total_minutes=Sum(
                'task__duration_minutes'
            )
        )
    )

    for item in planner_data:
        topic_id = item['task__topic_id']

        planner_minutes_by_topic[topic_id] = (
            item['total_minutes'] or 0
        )

    # --------------------------------------------------
    # CALCULATE SUBJECT AND OVERALL PROGRESS
    # --------------------------------------------------

    subject_stats = {}

    total_teaching_minutes = 0
    completed_teaching_minutes = 0

    for topic in topics:
        estimated = max(
            1,
            int(topic.estimated_minutes or 30),
        )

        # Manual progress percentage
        manual_percent = min(
            100.0,
            max(
                0.0,
                progress_by_topic.get(
                    topic.id,
                    0.0,
                ),
            ),
        )

        # Planner completion minutes
        planner_minutes = max(
            0.0,
            float(
                planner_minutes_by_topic.get(
                    topic.id,
                    0,
                ) or 0
            ),
        )

        # --------------------------------------------------
        # MASTERED TOPICS ARE ALWAYS 100% COMPLETE
        # --------------------------------------------------

        if status_by_topic.get(topic.id) == 'mastered':
            completion_percent = 100.0

        else:
            planner_percent = min(
                100.0,
                planner_minutes * 100.0 / estimated,
            )

            completion_percent = max(
                manual_percent,
                planner_percent,
            )

        # Convert percentage into credited minutes.
        credited_minutes = (
            estimated * completion_percent / 100.0
        )

        credited_minutes = min(
            estimated,
            max(0.0, credited_minutes),
        )

        subject = topic.unit.subject

        if subject.id not in subject_stats:
            subject_stats[subject.id] = {
                'code': subject.code,
                'title': subject.title,
                'total_teaching_minutes': 0,
                'completed_teaching_minutes': 0,
            }

        subject_stats[subject.id][
            'total_teaching_minutes'
        ] += estimated

        subject_stats[subject.id][
            'completed_teaching_minutes'
        ] += credited_minutes

        total_teaching_minutes += estimated
        completed_teaching_minutes += credited_minutes

    # --------------------------------------------------
    # FORMAT SUBJECT PROGRESS
    # --------------------------------------------------

    subjects_data = []

    for subject in subject_stats.values():
        subject_total = subject[
            'total_teaching_minutes'
        ]

        subject_completed = subject[
            'completed_teaching_minutes'
        ]

        subject_percent = (
            subject_completed * 100.0 / subject_total
            if subject_total > 0
            else 0.0
        )

        subjects_data.append({
            'code': subject['code'],
            'title': subject['title'],
            'total_teaching_minutes': round(
                subject_total
            ),
            'completed_teaching_minutes': round(
                subject_completed
            ),
            'completion_percent': round(
                subject_percent,
                1,
            ),
        })

    # --------------------------------------------------
    # OVERALL SYLLABUS PROGRESS
    # --------------------------------------------------

    overall_completion_percent = (
        completed_teaching_minutes
        * 100.0
        / total_teaching_minutes
        if total_teaching_minutes > 0
        else 0.0
    )

    # --------------------------------------------------
    # RESPONSE
    # --------------------------------------------------

    return Response({
        'today': today.isoformat(),
        'completed_sessions': completed_sessions,

        'weekly_study_minutes': weekly_study_minutes,

        'weekly_study_hours': weekly_study_hours,
        'weekly_study_minutes': int(weekly_study_minutes),
        'completed_sessions': completed_sessions,

        'tasks': {
            'completed': completed_tasks,
            'pending': pending_tasks,
        },

        'flashcards_due': flashcards_due,

        'syllabus_progress': {
            'total_teaching_minutes': round(
                total_teaching_minutes
            ),

            'completed_teaching_minutes': round(
                completed_teaching_minutes
            ),

            'completion_percent': round(
                overall_completion_percent,
                1,
            ),
        },

        'subjects': subjects_data,
    })

# ------------------------------------------------------
# PREFERENCES
# ------------------------------------------------------

@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def preferences(request):
    obj = AppPreferences.objects.first()

    if obj is None:
        obj = AppPreferences.objects.create()

    if request.method == 'PATCH':
        allowed = {
            'lock_timeout_minutes': (1, 60),
            'daily_goal_minutes': (1, 1440),
            'reminder_advance_minutes': (0, 1440),
        }

        for field, (minimum, maximum) in allowed.items():
            if field in request.data:
                value = int(request.data[field])

                if not minimum <= value <= maximum:
                    return Response(
                        {
                            'detail': (
                                f'{field} must be between '
                                f'{minimum} and {maximum}.'
                            )
                        },
                        status=400,
                    )

                setattr(obj, field, value)

        if 'notifications_enabled' in request.data:
            obj.notifications_enabled = bool(
                request.data['notifications_enabled']
            )

        obj.save()

    return Response({
        'lock_timeout_minutes': obj.lock_timeout_minutes,
        'daily_goal_minutes': obj.daily_goal_minutes,
        'notifications_enabled': obj.notifications_enabled,
        'reminder_advance_minutes': obj.reminder_advance_minutes,
        'updated_at': obj.updated_at,
    })


# ------------------------------------------------------
# PROGRESS ANALYTICS
# ------------------------------------------------------

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def progress_analytics(request):
    today = timezone.localdate()

    try:
        days = int(request.query_params.get('days', 7))
    except (TypeError, ValueError):
        return Response(
            {'detail': 'days must be 7, 30 or 90.'},
            status=400,
        )

    if days not in (7, 30, 90):
        return Response(
            {'detail': 'days must be 7, 30 or 90.'},
            status=400,
        )

    start = today - timedelta(days=days - 1)
    daily = []

    for offset in range(days):
        day = start + timedelta(days=offset)

        minutes = (
            Task.objects
            .filter(
                status='done',
                due_at__date=day,
            )
            .aggregate(total=Sum('duration_minutes'))['total'] or 0
        )

        daily.append({
            'date': str(day),
            'minutes': minutes,
        })

    total = sum(item['minutes'] for item in daily)

    prefs = (
        AppPreferences.objects.first()
        or AppPreferences.objects.create()
    )

    return Response({
        'period_days': days,
        'daily_study': daily,
        'total_minutes': total,
        'average_minutes_per_day': round(total / days, 1),
        'daily_goal_minutes': prefs.daily_goal_minutes,
        'goal_completion_percent': (
            round(
                total / (prefs.daily_goal_minutes * days) * 100
            )
            if prefs.daily_goal_minutes else 0
        ),
        'completed_sessions': Task.objects.filter(
            status='done',
            due_at__date__gte=start,
            due_at__date__lte=today,
        ).count(),
    })