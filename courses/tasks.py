import os
import logging
import subprocess
from celery import shared_task
from celery.exceptions import Retry
from django.conf import settings
from django.core.cache import cache
from .models import Lesson, Course

logger = logging.getLogger(__name__)

@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    max_retries=5,
)
def transcode_lesson_video(self, lesson_id):
    """
    Convert the uploaded Lesson.video (MP4) into HLS segments, and generate a thumbnail.
    CPU-bound: offload to Celery worker with ffmpeg installed.
    """
    try:
        lesson = Lesson.objects.get(pk=lesson_id)
        src = lesson.video.path
        if not os.path.exists(src):
            raise FileNotFoundError(f"Source video not found: {src}")

        # 1) generate HLS
        hls_dir = os.path.join(settings.MEDIA_ROOT, "videos", str(lesson_id), "hls")
        os.makedirs(hls_dir, exist_ok=True)
        hls_index = os.path.join(hls_dir, "index.m3u8")

        cmd_hls = [
            "ffmpeg", "-y", "-i", src,
            "-profile:v", "baseline", "-level", "3.0",
            "-start_number", "0", "-hls_time", "10", "-hls_list_size", "0",
            hls_index
        ]
        subprocess.check_call(cmd_hls)
        lesson.hls_url = f"{settings.MEDIA_URL}videos/{lesson_id}/hls/index.m3u8"

        # 2) snapshot thumbnail at 5s
        thumb_dir = os.path.dirname(src)
        thumb_path = os.path.splitext(src)[0] + "_thumb.jpg"
        cmd_thumb = ["ffmpeg", "-y", "-i", src, "-ss", "00:00:05.000", "-vframes", "1", thumb_path]
        subprocess.check_call(cmd_thumb)
        lesson.thumbnail = os.path.relpath(thumb_path, settings.MEDIA_ROOT)

        lesson.save()
    except Exception as exc:
        logger.exception(f"Error transcoding video for lesson {lesson_id}")
        # retry on transient errors
        raise self.retry(exc=exc)

@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=3,
)


def rebuild_course_index(self, course_id):
    """
    Refresh search index and purge CDN cache for a course after create/update.
    """
    pass

