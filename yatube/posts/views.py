from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User


def addition_paginator(queryset, request):
    # Внедрение паджинатора
    paginator = Paginator(queryset, settings.NUM_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return {'page_obj': page_obj}


def index(request):
    # Главная страница
    post_list = Post.objects.all()
    template = 'posts/index.html'
    context_title = addition_paginator(post_list, request)
    return render(request, template, context_title)


def group_posts(request, slug):
    # Групповая страница
    group = get_object_or_404(Group, slug=slug)
    groups = group.posts.all()
    template = 'posts/group_list.html'
    context = {
        'group': group,
        'posts': groups,
    }
    context.update(addition_paginator(groups, request))
    return render(request, template, context)


def profile(request, username):
    # Страница профиля
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    following = request.user.is_authenticated
    if following:
        following = author.following.filter(user=request.user).exists()
    template = 'posts/profile.html'
    context = {
        'author': author,
        'following': following
    }
    context.update(addition_paginator(posts, request))
    return render(request, template, context)


def post_detail(request, post_id):
    # Подробная информация о посте
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    comments = Comment.objects.filter(post=post)
    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }
    template = 'posts/post_detail.html'
    return render(request, template, context)


@login_required
def post_create(request):
    # Создание поста
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        create_post = form.save(commit=False)
        create_post.author = request.user
        create_post.save()
        return redirect('posts:profile', create_post.author)
    template = 'posts/create_post.html'
    context = {'form': form}
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    # Редактирование поста
    edit_post = get_object_or_404(Post, id=post_id)
    if request.user != edit_post.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=edit_post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    template = 'posts/create_post.html'
    context = {'form': form, 'is_edit': True}
    return render(request, template, context)

@login_required
def add_comment(request, post_id):
    # Добавление комментария
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    comments = Comment.objects.filter(post=post)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('posts:post_detail', post_id=post_id)

    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts:post_detail', context)

@login_required
def follow_index(request):
    posts = Post.objects.filter(
        author__following__user=request.user)
    context = addition_paginator(posts, request)
    template = 'posts/follow.html'
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    # Подписка
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    template = 'posts:profile'
    return redirect(template, author)


@login_required
def profile_unfollow(request, username):
    # Отписка
    user_follower = get_object_or_404(
        Follow,
        user=request.user,
        author__username=username
    )
    user_follower.delete()
    template = 'posts:profile'
    return redirect(template, username)
