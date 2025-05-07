from django.urls import path
from .views import (
    ScormPackageUploadView,
    ScoListView,
    LaunchScoView,
    RuntimePingView,
    ScormPackageListByCourse
)

urlpatterns = [
    path("packages/", ScormPackageUploadView.as_view(), name="scorm-upload"),
    path("packages/<int:package_id>/scos/", ScoListView.as_view(), name="scorm-sco-list"),
    path("launch/<int:sco_id>/", LaunchScoView.as_view(), name="scorm-launch"),
    path("runtime/<int:sco_id>/", RuntimePingView.as_view(), name="scorm-runtime"),
    path(
      "courses/<int:course_id>/packages/",ScormPackageListByCourse.as_view(), name="scorm-packages-by-course"),
]