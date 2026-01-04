"""
Django admin configuration for app models
"""
from django.contrib import admin
from .models import (
    AccessCode, Wallet, Category, Transaction, 
    Budget, RecurringTransaction
)


@admin.register(AccessCode)
class AccessCodeAdmin(admin.ModelAdmin):
    list_display = ['id', 'is_active', 'created_at', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ['name', 'wallet_type', 'balance', 'exclude_from_total', 'created_at']
    list_filter = ['wallet_type', 'exclude_from_total']
    search_fields = ['name']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'created_at']
    search_fields = ['name']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['date', 'transaction_type', 'amount', 'category', 'wallet', 'description']
    list_filter = ['transaction_type', 'date', 'category', 'wallet']
    search_fields = ['description', 'contact_person']
    date_hierarchy = 'date'
    readonly_fields = ['created_at', 'updated_at', 'qdrant_point_id']


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['category', 'amount', 'period', 'start_date', 'end_date', 'is_active', 'get_spent_display']
    list_filter = ['period', 'is_active', 'start_date']
    search_fields = ['category__name']
    
    def get_spent_display(self, obj):
        spent = obj.get_spent_amount()
        percentage = obj.get_percentage_used()
        return f"{spent:,.0f} / {obj.amount:,.0f} ({percentage:.1f}%)"
    get_spent_display.short_description = "Đã chi / Tổng"


@admin.register(RecurringTransaction)
class RecurringTransactionAdmin(admin.ModelAdmin):
    list_display = ['name', 'amount', 'frequency', 'next_run_date', 'is_active', 'wallet', 'category']
    list_filter = ['frequency', 'is_active', 'transaction_type', 'next_run_date']
    search_fields = ['name', 'description']

