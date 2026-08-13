from django.contrib import admin
from .models import Category, Food, Offer, Review

# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "name",
    )


@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "category",
        "price",
        "discount_percentage",
        "food_type",
        "is_available",
        "is_special",
        "is_featured",
    )

    list_filter = (
        "category",
        "food_type",
        "spice_level",
        "is_available",
        "is_special",
        "is_featured",
    )

    search_fields = (
        "name",
        "description",
    )

    prepopulated_fields = {
        "slug": ("name",)
    }


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "discount_type",
        "discount_value",
        "start_at",
        "end_at",
        "is_active",
    )

    list_filter = (
        "discount_type",
        "is_active",
    )

    search_fields = (
        "name",
        "coupon_code",
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "food",
        "rating",
        "is_approved",
        "created_at",
    )

    list_filter = (
        "rating",
        "is_approved",
    )

    search_fields = (
        "food__name",
        "user__username",
        "comment",
    )