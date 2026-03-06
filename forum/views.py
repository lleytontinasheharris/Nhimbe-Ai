"""Forum views - List, Detail, Create, Search"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from .models import Category, Post, Comment
from .forms import PostForm, CommentForm
from django.http import JsonResponse


def forum_home(request):
    """Forum landing page showing categories and recent posts"""
    categories = Category.objects.annotate(
        total_posts=Count('posts')
    ).order_by('order')
    recent_posts = Post.objects.select_related('author', 'category')[:10]

    context = {
        'categories': categories,
        'recent_posts': recent_posts,
    }
    return render(request, 'forum/home.html', context)


def category_detail(request, slug):
    """Show all posts in a category"""
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(category=category).select_related('author').annotate(
        total_comments=Count('comments')
    )

    context = {
        'category': category,
        'posts': posts,
    }
    return render(request, 'forum/category_detail.html', context)


def post_detail(request, slug):
    """Show a single post with comments"""
    post = get_object_or_404(
        Post.objects.select_related('author', 'category'),
        slug=slug
    )

    # Increment view count
    Post.objects.filter(pk=post.pk).update(views=post.views + 1)

    comments = post.comments.select_related('author')
    comment_form = CommentForm()

    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, 'forum/post_detail.html', context)


@login_required
def create_post(request):
    """Create a new forum post"""
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Your post has been published.')
            return redirect('forum:post_detail', slug=post.slug)
    else:
        form = PostForm()

    return render(request, 'forum/create_post.html', {'form': form})


@login_required
def edit_post(request, slug):
    """Edit an existing post (author only)"""
    post = get_object_or_404(Post, slug=slug, author=request.user)

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Post updated successfully.')
            return redirect('forum:post_detail', slug=post.slug)
    else:
        form = PostForm(instance=post)

    return render(request, 'forum/edit_post.html', {'form': form, 'post': post})


@login_required
def delete_post(request, slug):
    """Delete a post (author only)"""
    post = get_object_or_404(Post, slug=slug, author=request.user)

    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post has been deleted.')
        return redirect('forum:home')

    return render(request, 'forum/delete_post.html', {'post': post})


@login_required
def add_comment(request, slug):
    """Add a comment to a post"""
    post = get_object_or_404(Post, slug=slug)

    if post.is_closed:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Discussion is closed'}, status=403)
        messages.error(request, 'This discussion is closed.')
        return redirect('forum:post_detail', slug=post.slug)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'ok', 'comment_id': comment.id})

            messages.success(request, 'Comment added.')
            return redirect('forum:post_detail', slug=post.slug)

    return redirect('forum:post_detail', slug=post.slug)


def forum_search(request):
    """Search forum posts"""
    query = request.GET.get('q', '').strip()
    results = []

    if query:
        results = Post.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        ).select_related('author', 'category').annotate(
            total_comments=Count('comments')
        )

    context = {
        'query': query,
        'results': results,
    }
    return render(request, 'forum/search.html', context)

def poll_comments(request, slug):
    """Return comments as JSON for polling"""
    post = get_object_or_404(Post, slug=slug)
    last_id = request.GET.get('last_id', 0)

    try:
        last_id = int(last_id)
    except (ValueError, TypeError):
        last_id = 0

    new_comments = post.comments.filter(id__gt=last_id).select_related('author')

    comments_data = []
    for comment in new_comments:
        comments_data.append({
            'id': comment.id,
            'author': comment.author.username,
            'content': comment.content,
            'created_at': comment.created_at.strftime('%d %b %Y, %H:%M'),
            'time_since': _timesince(comment.created_at),
        })

    return JsonResponse({
        'comments': comments_data,
        'total': post.comments.count(),
    })


def _timesince(dt):
    """Simple timesince helper for JSON responses"""
    from django.utils import timezone
    from datetime import timedelta

    now = timezone.now()
    diff = now - dt

    if diff < timedelta(minutes=1):
        return 'just now'
    elif diff < timedelta(hours=1):
        mins = int(diff.total_seconds() / 60)
        return f'{mins} minute{"s" if mins != 1 else ""} ago'
    elif diff < timedelta(days=1):
        hours = int(diff.total_seconds() / 3600)
        return f'{hours} hour{"s" if hours != 1 else ""} ago'
    elif diff < timedelta(days=30):
        days = diff.days
        return f'{days} day{"s" if days != 1 else ""} ago'
    else:
        months = int(diff.days / 30)
        return f'{months} month{"s" if months != 1 else ""} ago'