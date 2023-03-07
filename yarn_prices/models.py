from django.db import models

# Create your models here.
class Shop(models.Model):
    name = models.CharField(max_length=200, blank=True)
    url = models.URLField(blank=True)

    def __str__(self) -> str:
        return self.name


class YarnCategory(models.Model):
    name = models.CharField(max_length=200, blank=True)
    shop = models.ForeignKey('Shop', on_delete=models.PROTECT, blank=True)

    def __str__(self) -> str:
        return self.name

class YarnDetails(models.Model):
    yarn = models.ForeignKey('YarnCategory', on_delete=models.PROTECT, blank=True)
    price = models.FloatField(blank=True)
    date = models.DateField(auto_now_add=True, blank=True)

    def __str__(self) -> str:
        return self.yarn.shop.name

class ColorsAvailability(models.Model):
    yarn = models.ForeignKey('YarnCategory', on_delete=models.PROTECT, blank=True)
    code = models.IntegerField(blank=True)
    name = models.CharField(max_length=200, blank=True)
    availability = models.CharField(max_length=200, blank=True)

    def __str__(self) -> str:
        return self.name