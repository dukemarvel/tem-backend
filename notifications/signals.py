from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from allauth.account.signals import user_signed_up

from payments.models import Enrollment
from progress.models import LessonProgress, CourseProgress
from courses.models import Lesson

from .models import Notification
from .tasks import send_notification_email

User = get_user_model()

@receiver(user_signed_up)
def welcome_user(sender, request, user, **kwargs):
    # In-app notification
    Notification.objects.create(
        recipient=user,
        verb="Welcome to Acadamier! Please verify your email to get started."
    )
    # Email
    send_notification_email.delay(
        user.email,
        "Welcome to Acadamier!",
        f"Hi {user.username}, welcome aboard! 🎉"
    )

@receiver(post_save, sender=Enrollment)
def enrollment_notification(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        course = instance.course
        verb = f"You’re now enrolled in “{course.title}”"
        Notification.objects.create(recipient=user, verb=verb)
        send_notification_email.delay(
            user.email,
            f"Enrollment confirmed: {course.title}",
            f"Congrats {user.username}! You’ve been enrolled in {course.title}."
        )

@receiver(post_save, sender=LessonProgress)
def lesson_progress_notification(sender, instance, **kwargs):
    if instance.is_completed:
        user = instance.user
        course = instance.lesson.course
        total = course.lessons.count()
        done = (
            LessonProgress.objects
            .filter(user=user, is_completed=True, lesson__course=course)
            .count()
        )
        verb = f"You’ve completed {done}/{total} lessons in “{course.title}”"
        Notification.objects.create(recipient=user, verb=verb)
        send_notification_email.delay(
            user.email,
            f"Lesson milestone: {course.title}",
            verb
        )

@receiver(post_save, sender=CourseProgress)
def course_completion_notification(sender, instance, **kwargs):
    if instance.percent == 100:
        user = instance.user
        course = instance.course
        verb = f"Congratulations! You’ve completed “{course.title}”"
        Notification.objects.create(recipient=user, verb=verb)
        send_notification_email.delay(
            user.email,
            f"Course completed: {course.title}",
            f"Well done {user.username}! Download your certificate at /api/v1/progress/certificates/"
        )

@receiver(post_save, sender=Lesson)
def new_lesson_published(sender, instance, created, **kwargs):
    if created:
        course = instance.course
        for enrollment in course.enrollments.all():
            user = enrollment.user
            verb = f"New lesson available: “{instance.title}” in {course.title}"
            Notification.objects.create(recipient=user, verb=verb)
            send_notification_email.delay(
                user.email,
                f"New lesson in {course.title}",
                f"Hi {user.username}, a new lesson “{instance.title}” has just been published."
            )
