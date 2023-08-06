from colorfield.fields import ColorField
from django.db import models
from django.utils.translation import gettext_lazy as _


class Asset(models.Model):
    title = models.CharField(_("title"), primary_key=True, max_length=200)
    picture = models.ImageField(_("picture"), upload_to="assets")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("asset")
        verbose_name_plural = _("assets")


class Parameter(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    name = models.CharField(_("name"), max_length=200)
    color = ColorField(verbose_name=_("color"))
    font_url = models.URLField(_("font url"))
    font_size = models.IntegerField(_("font size"), default=0)
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
