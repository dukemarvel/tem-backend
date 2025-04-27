from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Course, Lesson
from .tasks import rebuild_course_index, transcode_lesson_video

@receiver(post_save, sender=Course)
def on_course_saved(sender, instance, created, **kwargs):
    # whenever a course is created or updated, rebuild its search index & cache
    rebuild_course_index.delay(instance.id)
    

@receiver(post_save, sender=Lesson)
def on_lesson_saved(sender, instance, created, **kwargs):
    # if a new video file was attached, kick off the transcode task
    if created and instance.video:
        transcode_lesson_video.delay(instance.id)
