from django.contrib import admin
from .models import *
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models.config import Config


class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "email", "password")}),
        ("Personal info", {"fields": ("name", "phoneNumber")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "username", "name", "password1", 
                           "password2"),
            },
        ),
    )
    list_display = ("username", "email", "name", "phoneNumber", "is_staff", 
                    "is_superuser")
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("email", "username", "name", "phoneNumber")
    ordering = ("email", "name", "phoneNumber")
    filter_horizontal = (
        "groups",
        "user_permissions",
    )


User_ = get_user_model()

admin.site.register(User_, UserAdmin)
admin.site.register(Kyc)
admin.site.register(Card)
admin.site.register(Cart)
admin.site.register(Conversation)
admin.site.register(Message)
admin.site.register(Disco)
admin.site.register(BusinessUnit)
admin.site.register(Documentation)
admin.site.register(Document)
admin.site.register(Expertise)
admin.site.register(MeansOfIdentification)
admin.site.register(MeterRequest)
admin.site.register(NextOfKin)
admin.site.register(PaymentVendor)
# admin.site.register(Payment)
admin.site.register(Product)
admin.site.register(Purchase)
admin.site.register(Survey)
admin.site.register(TransactionLog)
admin.site.register(UserAddress)
admin.site.register(VerificationType)
admin.site.register(Verification)
admin.site.register(Wallet)
admin.site.register(WalletHistory)
admin.site.register(WorkOrder)
admin.site.register(WorkOrderMaterial)
admin.site.register(WorkOrderService)
admin.site.register(WorkOrderStatus)
admin.site.register(Config)
admin.site.register(PowerVend)
