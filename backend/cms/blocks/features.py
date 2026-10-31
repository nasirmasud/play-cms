from wagtail import blocks

ICON_CHOICES = [
    ("star", "Star"),
    ("zap", "Zap"),
    ("shield", "Shield"),
    ("heart", "Heart"),
    ("check", "Check"),
    ("sparkles", "Sparkles"),
    ("globe", "Globe"),
    ("rocket", "Rocket"),
    ("layers", "Layers"),
    ("settings", "Settings"),
]


class FeatureItemBlock(blocks.StructBlock):
    icon = blocks.ChoiceBlock(choices=ICON_CHOICES, default="star")
    heading = blocks.CharBlock(max_length=80)
    description = blocks.CharBlock(max_length=200)


class FeaturesBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=120, required=False)
    badge_text = blocks.CharBlock(max_length=40, required=False)
    items = blocks.ListBlock(FeatureItemBlock(), min_num=1, max_num=12)
    columns = blocks.ChoiceBlock(
        choices=[("2", "Two"), ("3", "Three"), ("4", "Four")],
        default="3",
    )
    background = blocks.ChoiceBlock(
        choices=[("none", "None"), ("muted", "Muted"), ("primary", "Primary")],
        default="none",
    )
    spacing = blocks.ChoiceBlock(
        choices=[("sm", "Small"), ("md", "Medium"), ("lg", "Large")],
        default="md",
    )

    class Meta:
        icon = "list-ul"
        label = "Features"
        label_format = "Features: {heading}"
