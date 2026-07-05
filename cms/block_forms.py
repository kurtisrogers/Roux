"""Visual form builders for CMS page blocks."""

import json

from django import forms

from cms.models import PageBlock


class BlockContentForm(forms.Form):
    """Base class – subclasses define fields matching block content JSON."""

    def to_content(self) -> dict:
        return self.cleaned_data

    @classmethod
    def from_content(cls, content: dict):
        return cls(initial=content)


class HeroBlockForm(BlockContentForm):
    title = forms.CharField(max_length=200)
    subtitle = forms.CharField(max_length=500, required=False)
    cta_text = forms.CharField(max_length=100, initial="Book Now")
    cta_url = forms.CharField(max_length=200, initial="/sessions/")


class RichTextBlockForm(BlockContentForm):
    body = forms.CharField(widget=forms.Textarea(attrs={"rows": 10}))


class CtaBlockForm(BlockContentForm):
    title = forms.CharField(max_length=200)
    text = forms.CharField(max_length=500, required=False)
    button_text = forms.CharField(max_length=100, initial="Get Started")
    button_url = forms.CharField(max_length=200, initial="/accounts/register/")


class ImageTextBlockForm(BlockContentForm):
    title = forms.CharField(max_length=200)
    text = forms.CharField(widget=forms.Textarea(attrs={"rows": 4}))
    image_url = forms.URLField(required=False)
    image_position = forms.ChoiceField(
        choices=[("left", "Left"), ("right", "Right")],
        initial="left",
    )


class FaqBlockForm(BlockContentForm):
    faq_json = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 8}),
        help_text='JSON array: [{"question": "...", "answer": "..."}]',
    )

    def clean_faq_json(self):
        raw = self.cleaned_data["faq_json"]
        try:
            items = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise forms.ValidationError("Invalid JSON") from exc
        if not isinstance(items, list):
            raise forms.ValidationError("Must be a JSON array")
        return items

    def to_content(self) -> dict:
        return {"items": self.cleaned_data["faq_json"]}

    @classmethod
    def from_content(cls, content: dict):
        return cls(initial={"faq_json": json.dumps(content.get("items", []), indent=2)})


class FeaturesBlockForm(FaqBlockForm):
    faq_json = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 8}),
        help_text='JSON array: [{"title": "...", "description": "..."}]',
        label="Features JSON",
    )

    def to_content(self) -> dict:
        return {"items": self.cleaned_data["faq_json"]}

    @classmethod
    def from_content(cls, content: dict):
        return cls(initial={"faq_json": json.dumps(content.get("items", []), indent=2)})


class TestimonialsBlockForm(FaqBlockForm):
    faq_json = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 8}),
        help_text='JSON array: [{"quote": "...", "author": "..."}]',
        label="Testimonials JSON",
    )

    def to_content(self) -> dict:
        return {"items": self.cleaned_data["faq_json"]}

    @classmethod
    def from_content(cls, content: dict):
        return cls(initial={"faq_json": json.dumps(content.get("items", []), indent=2)})


BLOCK_CONTENT_FORMS = {
    PageBlock.BlockType.HERO: HeroBlockForm,
    PageBlock.BlockType.RICH_TEXT: RichTextBlockForm,
    PageBlock.BlockType.CTA: CtaBlockForm,
    PageBlock.BlockType.IMAGE_TEXT: ImageTextBlockForm,
    PageBlock.BlockType.FAQ: FaqBlockForm,
    PageBlock.BlockType.FEATURES: FeaturesBlockForm,
    PageBlock.BlockType.TESTIMONIALS: TestimonialsBlockForm,
}


def get_content_form(block_type: str, data=None, content: dict | None = None):
    form_class = BLOCK_CONTENT_FORMS.get(block_type)
    if not form_class:
        return None
    if data is not None:
        return form_class(data)
    if content is not None:
        return form_class.from_content(content)
    return form_class()
