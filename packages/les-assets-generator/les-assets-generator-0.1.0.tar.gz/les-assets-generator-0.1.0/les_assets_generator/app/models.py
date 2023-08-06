from colorfield.fields import ColorField
from django.db import models
from django.utils.translation import gettext_lazy as _


class Asset(models.Model):
    title = models.CharField(primary_key=True, max_length=200, verbose_name=_("title"))
    picture = models.ImageField(upload_to="assets", verbose_name=_("picture"))

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("asset")
        verbose_name_plural = _("assets")


class Parameter(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, verbose_name=_("name"))
    color = ColorField(verbose_name=_("color"))
    font_url = models.URLField(verbose_name=_("font url"))
    font_size = models.IntegerField(default=0, verbose_name=_("font size"))
    x = models.IntegerField(default=0)
    y = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = (
            "asset",
            "name",
        )
        verbose_name = _("parameter")
        verbose_name_plural = _("parameters")
