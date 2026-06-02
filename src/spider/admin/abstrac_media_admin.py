from unfold.admin import ModelAdmin


class AbstractMediaAdmin(ModelAdmin):
    default_list_display = ("created_at",)
