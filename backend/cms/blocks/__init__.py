from .cta import CtaBlock
from .features import FeaturesBlock
from .fields import ApiImageChooserBlock, LinkBlock, SanitizedRichTextBlock
from .hero import HeroBlock
from .text import TextBlock

__all__ = [
    "BODY_BLOCKS",
    "ApiImageChooserBlock",
    "LinkBlock",
    "SanitizedRichTextBlock",
]

BODY_BLOCKS = [
    ("hero", HeroBlock()),
    ("text", TextBlock()),
    ("features", FeaturesBlock()),
    ("cta", CtaBlock()),
]
