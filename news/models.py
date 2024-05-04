from django.db import models

class News(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=50, choices=[
        ('candidate', 'Candidate'),
        ('client', 'Client'),
        ('recruiter', 'Recruiter')
    ])

    def __str__(self):
        return self.title
