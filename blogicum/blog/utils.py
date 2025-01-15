from django.db.models import Count
from django.utils import timezone


def get_published_posts(posts,
                        include_comment_count=False,
                        include_select_related=False):
    filtered_posts = posts.filter(
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True
    )

    if include_comment_count:
        filtered_posts = filtered_posts.annotate(
            comment_count=Count('comments')
        )

    if include_select_related:
        filtered_posts = filtered_posts.select_related(
            'category', 'author', 'location'
        )

    ordering = posts.model._meta.ordering
    if ordering:
        return filtered_posts.order_by(*ordering)

    return filtered_posts
