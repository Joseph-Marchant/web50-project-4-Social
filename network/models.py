from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    def __str__(self):
        return f"{self.username}"
    pass


class Post(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="posts")
    content = models.CharField(max_length=300)
    timestamp = models.DateTimeField(auto_now_add=True)
    like_count = models.IntegerField(default=0)

    def serialize(self):
        return {
            "id": self.id,
            "user": self.user,
            "content": self.content,
            "timestamp": self.timestamp,
            "likes": self.likes
        }
    
    def __str__(self):
        return f"{self.user} posted at {self.timestamp}"


class Follow(models.Model):
    follower = models.ForeignKey("User", on_delete=models.CASCADE, related_name="following")
    following = models.ForeignKey("User", on_delete=models.CASCADE, related_name="followers")

    def __str__(self):
        return f"{self.follower} is following {self.following}"


class Like(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="liked_posts")
    post = models.ForeignKey("Post", on_delete= models.CASCADE, related_name="likes")

    def __str__(self):
        return f"{self.user} like {self.post}"