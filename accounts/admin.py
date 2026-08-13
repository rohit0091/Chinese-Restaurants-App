from django.contrib import admin
from .models import CustomerProfile, Address


# Register your models here.


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "phone",
        "created_at",
    )

    search_fields = (
        "user__username",
        "user__email",
        "phone",
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "address_type",
        "city",
        "state",
        "is_default",
    )

    list_filter = (
        "address_type",
        "state",
        "is_default",
    )

    search_fields = (
        "user__username",
        "city",
        "pincode",
    )