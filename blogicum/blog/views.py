from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import CreateCommentForm, CreatePostForm
from .models import Category, Comment, Post, User
from .mixins import (
    CommentEditMixin,
    PostsEditMixin,
    CommentAccessMixin,
    AuthorRequiredMixin
)
from .utils import (get_published_posts)

PAGINATED_BY = 10


class PostDeleteView(PostsEditMixin,
                     LoginRequiredMixin,
                     AuthorRequiredMixin,
                     DeleteView):
    model = Post
    success_url = reverse_lazy('blog:index')


class PostUpdateView(PostsEditMixin,
                     LoginRequiredMixin,
                     AuthorRequiredMixin,
                     UpdateView):
    form_class = CreatePostForm
    success_url = reverse_lazy('blog:index')


class PostCreateView(PostsEditMixin,
                     LoginRequiredMixin,
                     CreateView):
    model = Post
    form_class = CreatePostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse('blog:profile', args=[self.request.user.username])


def form_valid(self, form):
    form.instance.author = self.request.user
    return super().form_valid(form)


def get_success_url(self) -> str:
    return reverse(
        'blog:profile',
        args=[self.request.user.username]
    )


class CommentCreateView(CommentEditMixin,
                        LoginRequiredMixin,
                        CreateView):
    model = Comment
    form_class = CreateCommentForm

    def form_valid(self, form):
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        form.instance.author = self.request.user
        return super().form_valid(form)


class CommentDeleteView(CommentAccessMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    success_url = reverse_lazy('blog:index')

    def get(self, request, *args, **kwargs):
        comment = self.get_object()
        return self.render_to_response({'comment': comment})

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CommentUpdateView(CommentAccessMixin,
                        UpdateView):
    model = Comment
    form_class = CreateCommentForm
    template_name = 'blog/comment.html'
    success_url = reverse_lazy('blog:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment'] = self.object
        return context

    def form_valid(self, form):
        return super().form_valid(form)


class AuthorProfileListView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    paginate_by = PAGINATED_BY

    def get_author(self):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_queryset(self):
        author = self.get_author()
        if self.request.user == author:
            return author.posts.all()
        else:
            return self.get_published_posts(author)

    def get_published_posts(self, author):
        return author.posts.filter(is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_author()
        for post in context['object_list']:
            post.comment_count = post.comments.count()
        return context


class BlogIndexListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    paginate_by = PAGINATED_BY

    queryset = get_published_posts(Post.objects.all())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for post in context['post_list']:
            post.comment_count = post.comments.count()

        return context


class BlogCategoryListView(ListView):
    model = Post
    template_name = 'blog/category.html'
    context_object_name = 'post_list'
    paginate_by = PAGINATED_BY

    def get_queryset(self):
        category_slug = self.kwargs['category_slug']
        category = get_object_or_404(Category, slug=category_slug,
                                     is_published=True)
        posts = get_published_posts(category.posts.all())
        return posts


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CreateCommentForm()
        context['comments'] = (
            self.get_object().comments.prefetch_related('author').all()
        )
        return context

    def get_object(self, queryset=None):
        post_id = self.kwargs[self.pk_url_kwarg]
        post = get_object_or_404(Post, pk=post_id)

        if self.request.user == post.author:
            return post

        return get_object_or_404(
            get_published_posts(Post.objects.all()),
            pk=post_id
        )
