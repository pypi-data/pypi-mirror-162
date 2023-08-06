from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from ckeditor.fields import RichTextField

from .base import Slide


class ForeignURLSlide(Slide):

    _supported_profiles = ["impressive", "surf"]

    url = models.URLField(max_length=255, verbose_name=_("URL"))

    def get_public_url(self, display=None, request=None):
        return self.url


class UploadedFileSlide(Slide):

    _supported_profiles = ["impressive"]

    TYPES = [
        "pdf",
        "jpg",
        "jpeg",
        "png",
        "tif",
        "bmp",
        "ppm",
        "avi",
        "mov",
        "mp4",
        "mkv",
        "webm",
        "ogv",
        "mpg",
        "mpeg",
        "ts",
        "flv",
    ]

    file = models.FileField(
        upload_to="buelleten/uploaded_file_slides/",
        validators=[FileExtensionValidator(allowed_extensions=TYPES)],
    )

    def get_public_url(self, display=None, request=None):
        return self.file.url


class StaticContentSlide(Slide):

    _supported_profiles = ["impressive", "surf"]

    content = RichTextField(verbose_name=_("Content"))
