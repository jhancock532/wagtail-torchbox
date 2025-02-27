import math
import string

from django import forms
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.dispatch import receiver
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property

from bs4 import BeautifulSoup
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    StreamFieldPanel,
)
from wagtail.core.fields import StreamField
from wagtail.core.models import Orderable, Page
from wagtail.core.signals import page_published
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index
from wagtail.snippets.edit_handlers import SnippetChooserPanel

from tbx.core.blocks import StoryBlock
from tbx.core.models import RelatedLink, Tag
from tbx.core.utils.cache import get_default_cache_control_decorator
from tbx.taxonomy.models import Service
from tbx.work.models import WorkPage


class BlogIndexPageRelatedLink(Orderable, RelatedLink):
    page = ParentalKey("blog.BlogIndexPage", related_name="related_links")


@method_decorator(get_default_cache_control_decorator(), name="serve")
class BlogIndexPage(Page):
    template = "patterns/pages/blog/blog_listing.html"

    subpage_types = ["BlogPage"]

    intro = models.TextField(blank=True)

    search_fields = Page.search_fields + [
        index.SearchField("intro"),
    ]

    def get_popular_tags(self):
        # Get a ValuesQuerySet of tags ordered by most popular (exclude 'planet-drupal' as this is effectively
        # the same as Drupal and only needed for the rss feed)
        popular_tags = (
            BlogPageTagSelect.objects.all()
            .exclude(tag__name="planet-drupal")
            .values("tag")
            .annotate(item_count=models.Count("tag"))
            .order_by("-item_count")
        )

        # Return first 10 popular tags as tag objects
        # Getting them individually to preserve the order
        return [Tag.objects.get(id=tag["tag"]) for tag in popular_tags[:10]]

    @property
    def blog_posts(self):
        # Get list of blog pages that are descendants of this page
        blog_posts = BlogPage.objects.live().descendant_of(self)

        # Order by most recent date first
        blog_posts = blog_posts.order_by("-date", "pk")

        return blog_posts

    def serve(self, request):
        # Get blog_posts
        blog_posts = self.blog_posts

        # Filter by related_service slug
        slug_filter = request.GET.get("filter")
        if slug_filter:
            blog_posts = blog_posts.filter(related_services__slug=slug_filter)

        # format for template
        blog_posts = [
            {
                "title": blog_post.title,
                "url": blog_post.url,
                "author": blog_post.first_author,
                "date": blog_post.date,
            }
            for blog_post in blog_posts
        ]

        # Pagination
        paginator = Paginator(blog_posts, 10)  # Show 10 blog_posts per page

        if request.is_ajax():
            # use page to filter
            page = request.GET.get("page")
            try:
                blog_posts = paginator.page(page)
            except PageNotAnInteger:
                blog_posts = paginator.page(1)
            except EmptyPage:
                blog_posts = None

            return render(
                request,
                "patterns/organisms/blog-listing/blog-listing.html",
                {"page": self, "blog_posts": blog_posts},
            )
        else:
            # return first page contents
            try:
                blog_posts = paginator.page(1)
            except EmptyPage:
                blog_posts = None

            related_services = Service.objects.all()

            return render(
                request,
                self.template,
                {
                    "page": self,
                    "blog_posts": blog_posts,
                    "related_services": related_services,
                },
            )

    content_panels = [
        FieldPanel("title", classname="full title"),
        FieldPanel("intro", classname="full"),
        InlinePanel("related_links", label="Related links"),
    ]

    promote_panels = [
        MultiFieldPanel(Page.promote_panels, "Common page configuration"),
    ]


# Blog page
class BlogPageRelatedLink(Orderable, RelatedLink):
    page = ParentalKey("blog.BlogPage", related_name="related_links")


# Currently hidden. These were used in the past and may be used again in the future
class BlogPageTagSelect(Orderable):
    page = ParentalKey("blog.BlogPage", related_name="tags")
    tag = models.ForeignKey(
        "torchbox.Tag", on_delete=models.CASCADE, related_name="blog_page_tag_select"
    )


class BlogPageAuthor(Orderable):
    page = ParentalKey("blog.BlogPage", related_name="authors")
    author = models.ForeignKey(
        "people.Author", on_delete=models.CASCADE, related_name="+",
    )

    panels = [
        SnippetChooserPanel("author"),
    ]


class BlogPage(Page):
    template = "patterns/pages/blog/blog_detail.html"

    parent_page_types = ["BlogIndexPage"]

    date = models.DateField("Post date")
    body = StreamField(StoryBlock())
    body_word_count = models.PositiveIntegerField(null=True, editable=False)

    feed_image = models.ForeignKey(
        "torchbox.TorchboxImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    listing_summary = models.TextField(blank=True)
    canonical_url = models.URLField(blank=True, max_length=255)
    related_services = ParentalManyToManyField(
        "taxonomy.Service", related_name="blog_posts"
    )

    search_fields = Page.search_fields + [
        index.SearchField("body"),
    ]

    def set_body_word_count(self):
        body_basic_html = self.body.stream_block.render_basic(self.body)
        body_text = BeautifulSoup(body_basic_html, "html.parser").get_text()
        remove_chars = string.punctuation + "“”’"
        body_words = body_text.translate(
            body_text.maketrans(dict.fromkeys(remove_chars))
        ).split()
        self.body_word_count = len(body_words)

    @property
    def related_blog_posts(self):
        services = self.related_services.all()

        # format for template
        return [
            {
                "title": blog_post.title,
                "url": blog_post.url,
                "author": blog_post.first_author,
                "date": blog_post.date,
            }
            for blog_post in BlogPage.objects.filter(related_services__in=services)
            .live()
            .distinct()
            .order_by("-first_published_at")
            .exclude(pk=self.pk)[:2]
        ]

    @cached_property
    def related_works(self):
        services = self.related_services.all()

        # Get the latest 2 work pages with the same service
        works = (
            WorkPage.objects.filter(related_services__in=services)
            .live()
            .public()
            .distinct()
            .order_by("-date")[:2]
        )
        return works

    @property
    def blog_index(self):
        ancestor = BlogIndexPage.objects.ancestor_of(self).order_by("-depth").first()

        if ancestor:
            return ancestor
        else:
            # No ancestors are blog indexes,
            # just return first blog index in database
            return BlogIndexPage.objects.first()

    @property
    def first_author(self):
        """Safely return the first author if one exists."""
        author = self.authors.first()
        if author:
            return author.author
        return None

    @property
    def read_time(self):
        if self.body_word_count:
            return math.ceil(self.body_word_count / 275)
        else:
            return "x"

    @property
    def type(self):
        return "BLOG POST"

    content_panels = [
        FieldPanel("title", classname="full title"),
        InlinePanel("authors", label="Author", min_num=1),
        FieldPanel("date"),
        StreamFieldPanel("body"),
        InlinePanel("related_links", label="Related links"),
    ]

    promote_panels = [
        MultiFieldPanel(Page.promote_panels, "Common page configuration"),
        ImageChooserPanel("feed_image"),
        FieldPanel("listing_summary"),
        FieldPanel("canonical_url"),
        FieldPanel("related_services", widget=forms.CheckboxSelectMultiple),
    ]


@receiver(page_published, sender=BlogPage)
def update_body_word_count_on_page_publish(instance, **kwargs):
    instance.set_body_word_count()
    instance.save(update_fields=["body_word_count"])
