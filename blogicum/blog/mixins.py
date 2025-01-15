from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse
from django.shortcuts import redirect

from .models import Comment, Post


class PostsEditMixin:
    model = Post
    template_name = 'blog/create.html'


class CommentEditMixin:
    model = Comment
    pk_url_kwarg = 'comment_pk'
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse('blog:post_detail', args=[self.kwargs['post_id']])


class AuthorRequiredMixin:
    model = Post
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        if self.request.user != post.author:
            return redirect('blog:post_detail',
                            post_id=self.kwargs[self.pk_url_kwarg])
        return super().dispatch(request, *args, **kwargs)


class CommentAuthorRequiredMixin:
    model = Comment
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        comment = self.get_object()
        if self.request.user != comment.author:
            return redirect('blog:post_detail', post_id=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

class CommentAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
    model = Comment
    pk_url_kwarg = 'comment_id'

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author or self.request.user.is_staff

    def handle_no_permission(self):
        return redirect('blog:index')
