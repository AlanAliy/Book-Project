from django.db import models


class Author(models.Model):
    first_name = models.CharField(verbose_name="First Name", max_length=50)
    last_name = models.CharField(verbose_name ="Last Name", max_length=50)
    birth_date = models.DateField(verbose_name="Birth Date")
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

