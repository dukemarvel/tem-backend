from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer
from .permissions import IsInstructor

class CourseViewSet(viewsets.ModelViewSet):

    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsInstructor()]
        # read-only actions: list, retrieve => open to any authenticated user
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        # auto-assign the instructor as the current user
        serializer.save(instructor=self.request.user)


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        # Let course owner (instructor) manage lessons
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsInstructor()]
        # read-only actions => any authenticated
        return [permissions.IsAuthenticated()]

    # explicit list() is not strictly required, but makes it clear
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        # require course_id
        course_id = request.data.get("course_id")
        if not course_id:
            return Response(
                {"detail": "course_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        # must be instructor on that course
        course = get_object_or_404(
            Course,
            id=course_id,
            instructor=request.user
        )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(course=course)
        return Response(serializer.data, status=status.HTTP_201_CREATED)