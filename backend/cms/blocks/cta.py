from wagtail import blocks

from .fields import LinkBlock


class CtaBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=120)
    subheading = blocks.CharBlock(max_length=300, required=False)
    cta = LinkBlock(required=False)
    variant = blocks.ChoiceBlock(
        choices=[("solid", "Solid"), ("outline", "Outline"), ("gradient", "Gradient")],
        default="solid",
    )
    background = blocks.ChoiceBlock(
        choices=[("none", "None"), ("muted", "Muted"), ("primary", "Primary")],
        default="none",
    )
    align = blocks.ChoiceBlock(
        choices=[("left", "Left"), ("center", "Center"), ("right", "Right")],
        default="center",
    )

    class Meta:
        icon = "bullhorn"
        label = "Call to action"
        label_format = "CTA: {heading}"
