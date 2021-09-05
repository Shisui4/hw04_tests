from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm, CommentForm
from .models import Group, Post, User, Comment


def index(request):
    posts_list = Post.objects.all().order_by('-pub_date')
    paginator = Paginator(posts_list, settings.CONSTANTA_POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).order_by('-pub_date')
    paginator = Paginator(posts, settings.CONSTANTA_POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'group': group,

    }
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts_profile = author.posts.all().order_by('-pub_date')
    posts_count = posts_profile.count()
    paginator = Paginator(posts_profile, settings.CONSTANTA_POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'author': author,
        'page_obj': page_obj,
        'posts_count': posts_count,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    selected_post = get_object_or_404(Post, id=post_id)
    author = selected_post.author
    posts_count = author.posts.count()

    context = {
        'selected_post': selected_post,
        'author': author,
        'posts_count': posts_count,
        'form': CommentForm,
        'comments': selected_post.comments.all(),
        'post_id': post_id
    }
    return render(request, 'posts/post_detail.html', context)


@login_required()
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST or None, files=request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', username=request.user.username)
        return render(request, 'posts/post_create.html', {'form': form})
    form = PostForm()
    return render(request, 'posts/post_create.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    is_edit = True
    if request.user == post.author:
        form = PostForm(request.POST or None, files=request.FILES or None, instance=post)
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id=post_id)
        return render(request, 'posts/post_create.html',
                      {'form': form, 'is_edit': is_edit, 'post_id': post_id})
    return redirect('posts:post_detail', post_id=post_id, )


@login_required
def add_comment(request, post_id):
    selected_post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = selected_post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)
