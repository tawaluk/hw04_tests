from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post, User


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
    template = 'posts/profile.html'
    context = {'author': author}
    context.update(addition_paginator(posts, request))
    return render(request, template, context)


def post_detail(request, post_id):
    # Подробная информация о посте
    post = get_object_or_404(Post, id=post_id)
    template = 'posts/post_detail.html'
    context = {'post': post}
    return render(request, template, context)


@login_required
def post_create(request):
    # Создание поста
    form = PostForm(request.POST or None)
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
    form = PostForm(request.POST or None, instance=edit_post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    template = 'posts/create_post.html'
    context = {'form': form, 'is_edit': True}
    return render(request, template, context)
