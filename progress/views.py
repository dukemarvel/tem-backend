from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from io import BytesIO
from django.http import HttpResponse
from reportlab.pdfgen import canvas


from .models import (
    LessonProgress, 
    CourseProgress, 
    ScormPackageProgress, 
    Certification, 
    ScormCertification
)


from .serializers import (
    LessonProgressSerializer,
    CourseProgressSerializer,
    ScormPackageProgressSerializer, 
    CertificationSerializer, 
    ScormCertificationSerializer
)

class LessonProgressViewSet(viewsets.ModelViewSet):
    queryset         = LessonProgress.objects.all()
    serializer_class = LessonProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        lp = self.get_object()
        lp.is_completed = True
        lp.save()
        return Response(LessonProgressSerializer(lp).data, status=status.HTTP_200_OK)


class CourseProgressViewSet(viewsets.ReadOnlyModelViewSet):
    queryset         = CourseProgress.objects.all()
    serializer_class = CourseProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class ScormPackageProgressViewSet(viewsets.ReadOnlyModelViewSet):
    queryset         = ScormPackageProgress.objects.all()
    serializer_class = ScormPackageProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)



class CertificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    List/Retrieve lesson certificates issued to the current user.
    """
    serializer_class   = CertificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # only show the logged-in user’s certificates
        return Certification.objects.filter(user=self.request.user)
    

    @action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        cert = self.get_object()
        # create PDF in memory
        buffer = BytesIO()
        p = canvas.Canvas(buffer)
        p.setTitle("Certificate of Completion")

        # Header
        p.setFont("Helvetica-Bold", 18)
        p.drawCentredString(300, 800, "Certificate of Completion")

        # Body
        p.setFont("Helvetica", 12)
        name = cert.user.get_full_name() or cert.user.username
        p.drawString(100, 750, f"Presented to: {name}")
        p.drawString(100, 730, f"For successfully completing lesson:")
        p.drawString(120, 710, f"\"{cert.lesson.title}\"")
        p.drawString(100, 690, f"Issued on: {cert.issued_at.date().isoformat()}")
        p.drawString(100, 670, f"Certificate ID: {cert.cert_id}")

        p.showPage()
        p.save()

        buffer.seek(0)
        response = HttpResponse(buffer, content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="certificate_{cert.cert_id}.pdf"'
        )
        return response


class ScormCertificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    List/Retrieve SCORM package certificates issued to the current user.
    """
    serializer_class   = ScormCertificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ScormCertification.objects.filter(user=self.request.user)
    

    @action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        scert = self.get_object()
        buffer = BytesIO()
        p = canvas.Canvas(buffer)
        p.setTitle("SCORM Completion Certificate")

        p.setFont("Helvetica-Bold", 18)
        p.drawCentredString(300, 800, "SCORM Completion Certificate")

        p.setFont("Helvetica", 12)
        name = scert.user.get_full_name() or scert.user.username
        p.drawString(100, 750, f"Presented to: {name}")
        p.drawString(100, 730, f"For successfully completing SCORM package:")
        p.drawString(120, 710, f"\"{scert.package.title}\"")
        p.drawString(100, 690, f"Issued on: {scert.issued_at.date().isoformat()}")
        p.drawString(100, 670, f"Certificate ID: {scert.cert_id}")

        p.showPage()
        p.save()

        buffer.seek(0)
        response = HttpResponse(buffer, content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="scorm_certificate_{scert.cert_id}.pdf"'
        )
        return response