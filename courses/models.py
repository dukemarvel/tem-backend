from django.db import models
from django.conf import settings

# ——— Helpers ——— #

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
    

class Category(models.Model):
    name   = models.CharField(max_length=100, unique=True)
    slug   = models.SlugField(max_length=100, unique=True)
    subtitle = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(
      upload_to="category_images/", 
      null=True, 
      blank=True, 
      help_text="Optional image for this category" 
  )
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="children",
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


# ——— Core Course Models ——— #

class Course(models.Model):
    BEGINNER, INTERMEDIATE, ADVANCED = "beginner", "intermediate", "advanced"
    DIFFICULTY_CHOICES = [
        (BEGINNER, "Beginner"),
        (INTERMEDIATE, "Intermediate"),
        (ADVANCED, "Advanced"),
    ]

    title         = models.CharField(max_length=255)
    subtitle      = models.CharField(max_length=255, blank=True)
    description   = models.TextField()
    about         = models.TextField(blank=True, help_text="Long-form description")
    learn         = models.JSONField(default=list, blank=True, help_text="What students will learn (list of strings)")
    price         = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    instructor    = models.ForeignKey(
                      settings.AUTH_USER_MODEL,
                      on_delete=models.CASCADE,
                      related_name="courses_taught"
                    )
    created_at    = models.DateTimeField(auto_now_add=True)
    language      = models.CharField(max_length=50, blank=True)

    default_access_days = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Leave blank for lifetime - set e.g. 14 or 30 for timed access"
    )

    # Marketing attrs
    promo_image   = models.ImageField(upload_to="course_images/", blank=True, null=True)
    promo_video   = models.FileField(upload_to="course_videos/", blank=True, null=True)
    tags          = models.ManyToManyField(Tag, blank=True, related_name="courses")
    difficulty    = models.CharField(
                      max_length=12,
                      choices=DIFFICULTY_CHOICES,
                      blank=True,
                      null=True
                    )
    duration      = models.DurationField(blank=True, null=True)
    prerequisites = models.ManyToManyField(
                      "self",
                      blank=True,
                      symmetrical=False,
                      related_name="dependent_courses"
                    )
    # Home‐feed flag
    featured      = models.BooleanField(default=False, help_text="Show on home feed carousel")

    # Structured category (hierarchical) 
    categories = models.ManyToManyField( 
        "Category", 
        blank=True, 
        related_name="courses" 
    )

    def __str__(self):
        return f"{self.title} (by {self.instructor.email})"

    @property
    def average_rating(self):
        return self.reviews.aggregate(models.Avg("rating"))["rating__avg"] or 0

class Module(models.Model):
    course      = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="modules")
    title       = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    order       = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.title} — {self.course.title}"

class Lesson(models.Model):
    module     = models.ForeignKey(
                    Module,
                    on_delete=models.CASCADE,
                    related_name="lessons",
                    null=True,
                    blank=True
                 )
    # back-compat: allow tests & view logic to pass `course=` directly
    course     = models.ForeignKey(
                    Course,
                    on_delete=models.CASCADE,
                    related_name="+",
                    null=True,
                    blank=True
                 )
    title      = models.CharField(max_length=255)
    content    = models.TextField()
    duration   = models.DurationField(blank=True, null=True, help_text="Estimated time for this lesson")
    video      = models.FileField(upload_to="videos/", blank=True, null=True)
    video_url  = models.URLField(blank=True, null=True)
    order      = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        if self.module:
            return f"Lesson: {self.title} in {self.module.title}"
        if self.course:
            return f"Lesson: {self.title} in {self.course.title}"
        return f"Lesson: {self.title}"

# ——— Reviews & Ratings ——— #

class Review(models.Model):
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course     = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="reviews")
    rating     = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1,6)])
    text       = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "course")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email} → {self.course.title}: {self.rating}⭐"

# ——— Wishlist ——— #

class WishlistItem(models.Model):
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wishlist")
    course     = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="wishlisted_by")
    added_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "course")

# ——— Promotions & Discounts ——— #

class Promotion(models.Model):
    course             = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="promotions")
    discount_percent   = models.PositiveSmallIntegerField()
    start_date         = models.DateField()
    end_date           = models.DateField()

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.discount_percent}% off {self.course.title}"



class Quiz(models.Model):
    # allow multiple quizzes per lesson
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="quizzes"
    )
    title = models.CharField(max_length=255)

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    order = models.PositiveIntegerField(default=0)

class Choice(models.Model):
    question   = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
    text       = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
