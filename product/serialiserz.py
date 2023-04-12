from rest_framework import serializers
from .models import Category, Product, Combo, Promotion, Menu

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class ComboSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True)

    class Meta:
        model = Combo
        fields = '__all__'

class PromotionSerializer(serializers.ModelSerializer):
    combos = ComboSerializer(many=True)
    products = ProductSerializer(many=True)

    class Meta:
        model = Promotion
        fields = '__all__'

class MenuSerializer(serializers.ModelSerializer):
    combos = ComboSerializer(many=True)
    products = ProductSerializer(many=True)
    promotions = PromotionSerializer(many=True)
    categories = CategorySerializer(many=True)

    class Meta:
        model = Menu
        fields = '__all__'
