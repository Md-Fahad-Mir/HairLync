from django.contrib import admin
from .models import SubscriptionPlan, Subscription


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'billing_cycle', 'price', 'max_employees', 'is_active')
    list_filter = ('billing_cycle', 'is_active')
    list_editable = ('is_active',)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'status', 'start_date', 'end_date', 'amount_paid')
    list_filter = ('status', 'plan')
    search_fields = ('user__email',)
    raw_id_fields = ('user',)
