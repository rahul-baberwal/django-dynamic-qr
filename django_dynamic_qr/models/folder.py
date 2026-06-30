from django.db import models
from django.conf import settings


class Folder(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="qr_folders"
    )
    name = models.CharField(max_length=255)
    color = models.CharField(max_length=7, default="#6366f1")  # hex colour for UI
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        unique_together = [("user", "name")]
        verbose_name = "Folder"
        verbose_name_plural = "Folders"

    def __str__(self):
        return self.name
