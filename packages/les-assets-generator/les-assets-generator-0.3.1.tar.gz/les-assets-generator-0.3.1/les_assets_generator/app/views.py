from io import BytesIO
from urllib.request import urlopen

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from PIL import Image, ImageDraw, ImageFont

from les_assets_generator.app.models import Asset, Parameter


def index(request):
    return redirect("https://github.com/lyon-esport/assets-generator")


def generate(request, title: str):
    asset = get_object_or_404(Asset.objects.select_related(), pk=title)
    params = Parameter.objects.select_related().filter(asset=asset)

    img = Image.open(asset.picture)
    draw = ImageDraw.Draw(img)

    for param in params:
        param_value = request.GET.get(param.name)
        if param_value is None:
            return HttpResponse(f"Missing GET parameter {param}", status=422)

        try:
            font = ImageFont.truetype(urlopen(param.font_url), param.font_size)
        except OSError:
            return HttpResponse(f"Font {param.font_url} not supported", status=422)
        draw.text((param.x, param.y), param_value, font=font, fill=param.color)

    byte_io = BytesIO()
    img.save(byte_io, "png")
    byte_io.seek(0)

    return HttpResponse(byte_io, content_type="image/png")
