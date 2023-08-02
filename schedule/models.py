from django.db import models


class Chat(models.Model):
    user = models.TextField()
    assistant = models.TextField()
    group = models.IntegerField(default=-1)
    writer = models.IntegerField(default=-1)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
