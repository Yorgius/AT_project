from django.db import models

# Create your models here.
class Shop(models.Model):
    name = models.CharField(max_length=200, blank=True)
    url = models.URLField(blank=True)

    def __str__(self) -> str:
        return self.name


class Yarn(models.Model):
    name = models.CharField(max_length=200, blank=True)
    price = models.FloatField(blank=True)
    date_added = models.DateField(auto_now_add=True)
    shop = models.ForeignKey('Shop', on_delete=models.PROTECT, blank=True)

    def __str__(self) -> str:
        return self.name
