from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email

class InstructorProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="instructorprofile"
    )
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"Instructor: {self.user.email}"

class StudentProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="studentprofile"
    )
    # you can add more student‑specific fields here

    def __str__(self):
        return f"Student: {self.user.email}"
