from rest_framework import serializers
from .models import Course, Lesson, Quiz, Question, Choice

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ["id", "title", "content", "video_url", "order", "created_at"]

class CourseSerializer(serializers.ModelSerializer):
    # Show lessons nested (read‑only by default for listing)
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ["id", "title", "description", "price", "instructor", "created_at", "lessons"]
        read_only_fields = ["instructor", "created_at"]

    def create(self, validated_data):
        # We’ll fill in `instructor` from request in the view
        return Course.objects.create(**validated_data)


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ["id","text","is_correct"]

class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True)
    class Meta:
        model = Question
        fields = ["id","text","order","choices"]

class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)
    class Meta:
        model = Quiz
        fields = ["id","title","lesson","questions"]

    def create(self, validated_data):
        qs = validated_data.pop("questions")
        quiz = Quiz.objects.create(**validated_data)
        for q in qs:
            chs = q.pop("choices")
            question = Question.objects.create(quiz=quiz, **q)
            for c in chs:
                Choice.objects.create(question=question, **c)
        return quiz

    def update(self, instance, validated_data):
        # naive full‑replacement: delete/recreate questions & choices
        instance.title = validated_data.get("title", instance.title)
        instance.save()
        instance.questions.all().delete()
        for q in validated_data.get("questions", []):
            chs = q.pop("choices")
            question = Question.objects.create(quiz=instance, **q)
            for c in chs:
                Choice.objects.create(question=question, **c)
        return instance