from rest_framework import generics, permissions, status, views
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from payments.permissions import IsEnrolled
from .permissions import IsCourseInstructor

from .models import ScormPackage, Sco, RuntimeData
from .serializers import (
    ScormPackageUploadSerializer,
    ScoSerializer,
    RuntimeDataSerializer,
)


# ───────── Upload & SCO list ───────── #

class ScormPackageUploadView(generics.CreateAPIView):
    queryset = ScormPackage.objects.all()
    serializer_class = ScormPackageUploadSerializer
    permission_classes = (permissions.IsAuthenticated, IsCourseInstructor)

    def perform_create(self, serializer):
        package = serializer.save(uploaded_by=self.request.user)
        # enqueue background processing
        from .tasks import extract_and_notify
        extract_and_notify.delay(package.id)

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx


class ScormPackageListByCourse(generics.ListAPIView):
    """
    List all SCORM packages attached to a given course.
    """
    serializer_class = ScormPackageUploadSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        course_id = self.kwargs["course_id"]
        # optionally enforce that request.user is instructor or enrolled
        return ScormPackage.objects.filter(course_id=course_id)


class ScoListView(generics.ListAPIView):
    serializer_class = ScoSerializer
    permission_classes = (permissions.IsAuthenticated, IsEnrolled())

    def get_queryset(self):
        return Sco.objects.filter(package_id=self.kwargs["package_id"]).order_by("sequence")

# ───────── Launch view ───────── #

class LaunchScoView(views.APIView):
    permission_classes = (permissions.IsAuthenticated, IsEnrolled())

    def get(self, request, sco_id):
        sco = get_object_or_404(Sco, id=sco_id)
        return render(request, "scorm_player/launch_iframe.html", {"sco": sco})

# ───────── Runtime API ───────── #
@method_decorator(csrf_exempt, name="dispatch")
class RuntimePingView(views.APIView):
    """
    POST → append/update runtime data sent by the SCO
    GET  → fetch current runtime snapshot for this user & SCO
    """
    permission_classes = (permissions.IsAuthenticated, IsEnrolled())

    def get_object(self, user, sco):
        obj, _ = RuntimeData.objects.get_or_create(user=user, sco=sco, attempt=1)
        return obj

    def get(self, request, sco_id):
        sco = get_object_or_404(Sco, id=sco_id)
        rd = self.get_object(request.user, sco)
        return Response(RuntimeDataSerializer(rd).data)

    def post(self, request, sco_id):
        sco = get_object_or_404(Sco, id=sco_id)
        rd = self.get_object(request.user, sco)

        serializer = RuntimeDataSerializer(rd, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        # Merge incoming CMI values with existing data
        rd.data.update(serializer.validated_data.get("data", {}))
        rd.save()

        return Response(RuntimeDataSerializer(rd).data, status=status.HTTP_202_ACCEPTED)