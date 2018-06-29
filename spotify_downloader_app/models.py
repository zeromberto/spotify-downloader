from django.db import models


class Token(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=128, unique=True)
    change_date = models.DateTimeField(auto_now_add=True, blank=True)
