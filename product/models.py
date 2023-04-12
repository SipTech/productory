from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Product(models.Model):
    name = models.CharField(max_length=255, unique=True)
    price = models.FloatField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Combo(models.Model):
    name = models.CharField(max_length=255, unique=True)
    price = models.FloatField()
    products = models.ManyToManyField(Product)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Promotion(models.Model):
    name = models.CharField(max_length=255, unique=True)
    price = models.FloatField()
    combos = models.ManyToManyField(Combo)
    products = models.ManyToManyField(Product)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Menu(models.Model):
    combos = models.ManyToManyField(Combo)
    products = models.ManyToManyField(Product)
    promotions = models.ManyToManyField(Promotion)
    categories = models.ManyToManyField(Category)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
