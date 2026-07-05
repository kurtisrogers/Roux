import pytest

from cms.block_forms import HeroBlockForm, get_content_form
from cms.block_renderer import render_block
from cms.models import PageBlock
from tests.factories import OrganisationFactory


@pytest.mark.django_db
class TestBlockForms:
    def test_hero_form_to_content(self):
        form = HeroBlockForm(
            data={
                "title": "Welcome",
                "subtitle": "Great care",
                "cta_text": "Book",
                "cta_url": "/sessions/",
            }
        )
        assert form.is_valid()
        assert form.to_content()["title"] == "Welcome"

    def test_get_content_form_unknown_returns_none(self):
        assert get_content_form("session_list") is None


@pytest.mark.django_db
class TestBlockRenderer:
    def test_render_hero_block(self):
        org = OrganisationFactory()
        block = PageBlock(
            block_type=PageBlock.BlockType.HERO,
            content={
                "title": "Hello",
                "subtitle": "World",
                "cta_text": "Go",
                "cta_url": "/",
            },
        )
        html = render_block(block, org)
        assert "Hello" in html
        assert "World" in html

    def test_render_features_block(self):
        org = OrganisationFactory()
        block = PageBlock(
            block_type=PageBlock.BlockType.FEATURES,
            content={"items": [{"title": "A", "description": "B"}]},
        )
        html = render_block(block, org)
        assert "A" in html
