from rest_framework import serializers
from .models import (
    Course, Lesson, Quiz, Question, Choice,
    Tag, Module, Review, Promotion, Category
    )

# ─── Tag ────────────────────────────────────────────────────────────────

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]

# ─── Category ───────────────────────────────────────────────────────────

class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "parent", "children"]

    def get_children(self, obj):
        return CategorySerializer(obj.children.all(), many=True).data

# ─── Promotion ─────────────────────────────────────────────────────────

class PromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promotion
        fields = ["id", "course", "discount_percent", "start_date", "end_date"]


# ─── Module & Lesson ───────────────────────────────────────────────────

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = [
            "id", "module", "course",  # <— added
            "title", "content", "video_url", "order", "created_at"
        ]
        read_only_fields = ["created_at"]


class ModuleSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = ["id", "course", "title", "description", "order", "lessons"]
        read_only_fields = ["lessons"]


# ─── Review ────────────────────────────────────────────────────────────

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.id")

    class Meta:
        model = Review
        fields = ["id", "user", "course", "rating", "text", "created_at"]
        read_only_fields = ["user", "created_at"]



class CourseSerializer(serializers.ModelSerializer):
    # Show lessons nested (read‑only by default for listing)
    lessons = LessonSerializer(many=True, read_only=True)
    categories = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Category.objects.all(),
        required=False
    )
    expires_at = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ["id", "title", "description", "price", "instructor", "categories", "featured", "created_at", "expires_at", "lessons"]
        read_only_fields = ["instructor", "created_at"]

    
    def get_expires_at(self, obj):
        """Return ISO timestamp (or None) for the current user’s enrollment."""
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None
        en = obj.enrollments.filter(user=request.user).first()
        if not en or not en.access_expires: 
            return None 
        # Always ISO-8601 string so tests & JS code can treat it uniformly 
        return en.access_expires.isoformat()

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