import os
from urllib import parse

from colorfield.fields import ColorField
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Asset(models.Model):
    title = models.CharField(_("title"), primary_key=True, max_length=200)
    picture = models.ImageField(_("picture"), upload_to="assets")

    def __str__(self):
        return self.title

    def generate_example_url(self):
        url = ""
        args = {}
        params = self.assets.all()
        for param in params:
            args[param.name] = "test"
        if len(params) > 0:
            url = f"{os.environ['DEFAULT_DOMAIN']}{reverse('generate', kwargs={'title': self.title})}?{parse.urlencode(args)}"
        return url

    class Meta:
        verbose_name = _("asset")
        verbose_name_plural = _("assets")


class Parameter(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="assets")
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
