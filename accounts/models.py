from django.db import models
from django.contrib.auth.models import User

class Genre(models.TextChoices):
    FANTASY = 'Фантастика'
    DETECTIVE = 'Детектив'
    THRILLER = 'Трилер'
    HISTORY = 'Історія'
    ROMANCE = 'Романтика'
    OTHER = 'Інше'

class Work(models.Model):
    title = models.CharField(max_length=200)
    genre = models.CharField(max_length=50, choices=Genre.choices)
    published_at = models.DateTimeField(auto_now_add=True)
    rating = models.PositiveIntegerField(default=0)  # 0–100
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='works')
    content = models.TextField()

    def __str__(self):
        return self.title

    @property
    def average_rating(self):
        ratings = self.ratings.all()
        if ratings:
            return round(sum(r.value for r in ratings) / ratings.count(), 1)
        return 0

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    work = models.ForeignKey(Work, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Коментар від {self.user.username if self.user else "Анонім"} до "{self.work.title}"'

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    work = models.ForeignKey(Work, on_delete=models.CASCADE, related_name='ratings')
    value = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])

    class Meta:
        unique_together = ('user', 'work')