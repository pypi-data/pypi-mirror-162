from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from les_assets_generator.app.models import Asset, Parameter


class ParameterTabularInline(admin.TabularInline):
    model = Parameter
    extra = 1


class AssetAdmin(admin.ModelAdmin):
    inlines = [
        ParameterTabularInline,
    ]
    readonly_fields = ("example_url",)
    list_display = (
        "title",
        "example_url",
    )

    @admin.display(description=_("example url"))
    def example_url(self, instance):
        if instance.title:
            r = instance.generate_example_url()
        else:
            message = _("Can't determine example URL for now")
            r = mark_safe(f"<span>{message}</span>")
        return r


admin.site.register(Asset, AssetAdmin)
