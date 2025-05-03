from rest_framework import viewsets, permissions, status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Course, Lesson, Quiz
from payments.permissions import IsEnrolled

from .serializers import (
    CourseSerializer, LessonSerializer,
    QuizSerializer
)
from .permissions import IsInstructor, IsOwnerInstructor

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsInstructor(), IsOwnerInstructor()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        # make current user the instructor
        serializer.save(instructor=self.request.user)

class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    parser_classes = (MultiPartParser, FormParser)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy", "upload_video"]:
            return [IsInstructor(), IsOwnerInstructor()]
        return [permissions.IsAuthenticated(), IsEnrolled()]


    def create(self, request, *args, **kwargs):

        course_id = request.data.get("course_id") or request.data.get("course")
        if not course_id:
            return Response(
                {"detail": "course_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        # ensure this user actually owns that course
        course = get_object_or_404(Course, id=course_id, instructor=request.user)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(course=course)
        return Response(serializer.data, status=status.HTTP_201_CREATED)



    @action(
        detail=True,
        methods=["post"],
        url_path="upload_video",
        url_name="upload_video"        # ← make the reverse name use an underscore
    )
    def upload_video(self, request, pk=None):
        lesson = self.get_object()
        file = request.FILES.get("video")
        if not file:
            return Response({"detail":"No file provided"}, status=400)
        
        # compute exactly where this file *would* be saved...
        storage = lesson.video.field.storage
        path = lesson.video.field.generate_filename(lesson, file.name)
        # ...and always delete whatever’s there first
        storage.delete(path)
        # now save under the original name
        lesson.video.save(file.name, file)
        lesson.save()
        return Response({"video_url": lesson.video.url})

class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer

    def get_permissions(self):
        if self.action in ["create","update","partial_update","destroy"]:
            return [IsInstructor(), IsOwnerInstructor()]
        return [permissions.IsAuthenticated(), IsEnrolled()]
    


class QuizSubmissionView(viewsets.ViewSet):
    permission_classes = (permissions.IsAuthenticated, IsEnrolled)

    @action(detail=True, methods=["post"], url_path="submit")
    def submit(self, request, pk=None):
        quiz = get_object_or_404(Quiz, pk=pk)
        answers = request.data.get("answers", {})
        total = quiz.questions.count()
        correct = 0
        for q in quiz.questions.all():
            selected = answers.get(str(q.id))
            if selected and q.choices.filter(id=selected, is_correct=True).exists():
                correct += 1
        score = (correct/total)*100 if total else 0
        return Response({"score": score, "total": total, "correct": correct})
