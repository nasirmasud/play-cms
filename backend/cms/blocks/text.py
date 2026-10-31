from wagtail import blocks

from .fields import SanitizedRichTextBlock


class TextBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=120, required=False)
    content = SanitizedRichTextBlock()
    align = blocks.ChoiceBlock(
        choices=[("left", "Left"), ("center", "Center"), ("right", "Right")],
        default="left",
    )
    max_width = blocks.ChoiceBlock(
        choices=[("sm", "Small"), ("md", "Medium"), ("lg", "Large")],
        default="md",
    )
    spacing = blocks.ChoiceBlock(
        choices=[("sm", "Small"), ("md", "Medium"), ("lg", "Large")],
        default="md",
    )

    class Meta:
        icon = "doc-full"
        label = "Text"
        label_format = "Text: {heading}"
