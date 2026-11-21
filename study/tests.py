from datetime import timedelta
from django.test import override_settings
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Device, Subject, Deck, Flashcard, Unit, Topic

@override_settings(SETUP_SECRET='test-setup-secret')
class StudyMateApiTests(APITestCase):
    def setUp(self):
        response = self.client.post('/api/v1/security/setup/', {
            'setup_secret': 'test-setup-secret', 'pin': '482915',
            'device_id': 'test-android-device', 'device_label': 'Test Android'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.recovery_key = response.data['recovery_key']
        self.access = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access}')

    def test_subjects_are_protected_and_accessible_after_pin_setup(self):
        Subject.objects.create(code='RM305', title='Research Methodology', category='compulsory', full_marks=100)
        response = self.client.get('/api/v1/subjects/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_device_token_is_bound_to_registered_device(self):
        Device.objects.filter(device_id='test-android-device').update(is_active=False)
        response = self.client.get('/api/v1/subjects/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_planner_accepts_past_date_and_completed_time_updates_dashboard(self):
        subject = Subject.objects.create(code='BOT301', title='Plant Biochemistry', category='core')
        unit = Unit.objects.create(subject=subject, title='Enzymes', sequence=1)
        topic = Topic.objects.create(unit=unit, title='Enzyme mechanisms', sequence=1, estimated_minutes=60)
        past = timezone.now() - timedelta(days=2)
        created = self.client.post('/api/v1/tasks/', {
            'title': 'Study enzyme mechanisms', 'subject': subject.id, 'topic': topic.id,
            'due_at': past.isoformat(), 'start_at': past.isoformat(),
            'duration_minutes': 45, 'status': 'todo', 'priority': 'medium'
        }, format='json')
        self.assertEqual(created.status_code, status.HTTP_201_CREATED, created.data)
        done = self.client.patch(f"/api/v1/tasks/{created.data['id']}/", {'status': 'done'}, format='json')
        self.assertEqual(done.status_code, status.HTTP_200_OK, done.data)
        dashboard = self.client.get('/api/v1/dashboard/')
        self.assertEqual(dashboard.status_code, status.HTTP_200_OK)
        self.assertEqual(dashboard.data['syllabus_progress']['completed_teaching_minutes'], 45)
        self.assertEqual(dashboard.data['syllabus_progress']['completion_percent'], 75)

    def test_flashcard_title_question_and_answer_are_saved(self):
        subject = Subject.objects.create(code='CHE303', title='Basic Biochemistry', category='elective')
        deck = Deck.objects.create(subject=subject, title='Proteins')
        response = self.client.post('/api/v1/flashcards/', {
            'deck': deck.id, 'title': 'Amino acids', 'front': 'What is an amino acid?',
            'back': 'An organic molecule with amino and carboxyl groups.', 'difficulty': 'medium'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data['title'], 'Amino acids')

    def test_flashcard_review_updates_next_due_date(self):
        subject = Subject.objects.create(code='BOT301', title='Plant Biochemistry and Biotechnology', category='core')
        deck = Deck.objects.create(subject=subject, title='Enzymes')
        card = Flashcard.objects.create(deck=deck, front='What is an enzyme?', back='A biological catalyst.')
        response = self.client.post('/api/v1/reviews/submit/', {'card': card.id, 'rating': 'good'}, format='json')
        self.assertEqual(response.status_code, 201)
        card.refresh_from_db()
        self.assertGreater(card.interval_days, 0)
