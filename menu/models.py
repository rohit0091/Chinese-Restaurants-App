from django.db import models

from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.






#------------------------------------------------------
#                          Category
# --------------------------------------------------------

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(
        upload_to='categories/',
        blank=True,
        null=True
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

#------------------------------------------------------
#                          FOOD
# --------------------------------------------------------

class Food(models.Model):

    FOOD_TYPE_CHOICES = [
        ('VEG', 'Vegetarian'),
        ('NON_VEG', 'Non-Vegetarian'),
    ]

    SPICE_LEVEL_CHOICES = [
        ('MILD', 'Mild'),
        ('MEDIUM', 'Medium'),
        ('HOT', 'Hot'),
        ('EXTRA_HOT', 'Extra Hot'),
    ]

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='foods'
    )

    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)

    description = models.TextField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(0.01)
        ]
    )

    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ]
    )

    calories = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    spice_level = models.CharField(
        max_length=20,
        choices=SPICE_LEVEL_CHOICES,
        default='MEDIUM'
    )

    food_type = models.CharField(
        max_length=20,
        choices=FOOD_TYPE_CHOICES
    )

    preparation_time = models.PositiveIntegerField(
        help_text='Preparation time in minutes'
    )

    image = models.ImageField(
        upload_to='foods/'
    )

    is_available = models.BooleanField(default=True)
    is_special = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def final_price(self):
        discount = (
            self.price * self.discount_percentage / 100
        )

        return self.price - discount

    def __str__(self):
        return self.name


#------------------------------------------------------
#                          OFFER
# --------------------------------------------------------

class Offer(models.Model):

    DISCOUNT_TYPE_CHOICES = [
        ("PERCENTAGE", "Percentage"),
        ("FIXED_AMOUNT", "Fixed Amount"),
    ]

    name = models.CharField(
        max_length=150
    )

    description = models.TextField()

    discount_type = models.CharField(
        max_length=20,
        choices=DISCOUNT_TYPE_CHOICES
    )

    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(0)
        ]
    )

    minimum_order_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[
            MinValueValidator(0)
        ]
    )

    maximum_discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(0)
        ]
    )

    coupon_code = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True
    )

    start_at = models.DateTimeField()

    end_at = models.DateTimeField()

    is_active = models.BooleanField(
        default=True
    )

    foods = models.ManyToManyField(
        Food,
        blank=True,
        related_name="offers"
    )

    categories = models.ManyToManyField(
        Category,
        blank=True,
        related_name="offers"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.name


#------------------------------------------------------
#                          REVIEW
# --------------------------------------------------------

class Review(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    food = models.ForeignKey(
        Food,
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.PROTECT,
        related_name="reviews"
    )

    rating = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )

    comment = models.TextField(
        blank=True
    )

    is_approved = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "food", "order"],
                name="unique_review_per_order_food"
            )
        ]

    def __str__(self):
        return f"{self.food.name} - {self.rating}/5"