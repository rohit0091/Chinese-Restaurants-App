from django.contrib import admin
from .models import (
    Order,
    OrderAddress,
    OrderItem,
    Payment,
    OrderStatusHistory,
)
# Register your models here.


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        "order_number",
        "user",
        "status",
        "total_amount",
        "created_at",
    )

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "order_number",
        "user__username",
        "user__email",
    )


@admin.register(OrderAddress)
class OrderAddressAdmin(admin.ModelAdmin):

    list_display = (
        "order",
        "full_name",
        "city",
        "state",
        "pincode",
    )

    search_fields = (
        "order__order_number",
        "full_name",
        "city",
        "pincode",
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):

    list_display = (
        "order",
        "food_name",
        "quantity",
        "unit_price",
        "subtotal",
    )

    search_fields = (
        "order__order_number",
        "food_name",
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):

    list_display = (
        "order",
        "payment_method",
        "payment_status",
        "amount",
        "created_at",
    )

    list_filter = (
        "payment_method",
        "payment_status",
    )

    search_fields = (
        "order__order_number",
        "transaction_id",
    )


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):

    list_display = (
        "order",
        "status",
        "changed_by",
        "created_at",
    )

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "order__order_number",
        "changed_by__username",
    )