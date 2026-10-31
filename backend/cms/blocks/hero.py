from wagtail import blocks

from .fields import ApiImageChooserBlock, LinkBlock


class HeroBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=120)
    badge_text = blocks.CharBlock(max_length=40, required=False)
    subheading = blocks.CharBlock(max_length=300, required=False)
    image = ApiImageChooserBlock(required=False)
    cta = LinkBlock(required=False)
    secondary_cta = LinkBlock(required=False)
    align = blocks.ChoiceBlock(
        choices=[("left", "Left"), ("center", "Center"), ("right", "Right")],
        default="center",
    )
    size = blocks.ChoiceBlock(
        choices=[("md", "Medium"), ("lg", "Large"), ("xl", "Extra large")],
        default="lg",
    )
    background = blocks.ChoiceBlock(
        choices=[
            ("none", "None"),
            ("muted", "Muted"),
            ("primary", "Primary"),
            ("image", "Image"),
        ],
        default="none",
    )
    spacing = blocks.ChoiceBlock(
        choices=[("sm", "Small"), ("md", "Medium"), ("lg", "Large")],
        default="md",
    )

    class Meta:
        icon = "pick"
        label = "Hero"
        label_format = "Hero: {heading}"
