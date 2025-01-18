from django.db import models

# Create your models here.

class User(models.Model):
    email=models.EmailField()
    password=models.CharField(max_length=20)
    is_active=models.BooleanField(default=True)

class Website(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE),
    url = models.URLField(unique=True)
    name=models.CharField(max_length=20)
    poolAfter=models.IntegerField(default=50)
    created_at = models.DateTimeField(auto_now_add=True)
    stop_monitoring = models.BooleanField(default=False)
    def delete(self, *args, **kwargs):
        # Set the stop flag to true before deleting
        self.stop_monitoring = True
        print("update the monitoring value")
        self.save()  # Save the change to stop monitoring
        
        super().delete(*args, **kwargs) 
    def __str__(self):
        return self.name

class StatusHistory(models.Model):
    website = models.ForeignKey(Website, on_delete=models.CASCADE)
    status = models.CharField(max_length=10)  # 'up' or 'down'
    checked_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.website