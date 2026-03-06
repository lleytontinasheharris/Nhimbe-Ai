"""Knowledge Base views"""

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Q, Count
from .models import ArticleCategory, Article, ArticleRating
from .forms import ArticleForm


def knowledge_home(request):
    """Knowledge base homepage"""
    categories = ArticleCategory.objects.annotate(
        total_articles=Count('articles', filter=Q(articles__is_published=True))
    )
    featured = Article.objects.filter(is_published=True, is_featured=True)[:3]
    recent = Article.objects.filter(is_published=True, is_featured=False)[:5]

    return render(request, 'knowledge/home.html', {
        'categories': categories,
        'featured': featured,
        'recent': recent,
    })


def category_articles(request, slug):
    """List articles in a category"""
    category = get_object_or_404(ArticleCategory, slug=slug)
    articles = Article.objects.filter(category=category, is_published=True)

    return render(request, 'knowledge/category_articles.html', {
        'category': category,
        'articles': articles,
    })


def article_detail(request, slug):
    """View a single article"""
    article = get_object_or_404(Article, slug=slug, is_published=True)
    
    # Increment view count
    article.increment_views()

    # Get related articles from same category
    related = []
    if article.category:
        related = Article.objects.filter(
            category=article.category,
            is_published=True
        ).exclude(pk=article.pk)[:3]

    # Get user's rating if logged in
    user_rating = None
    if request.user.is_authenticated:
        user_rating = article.user_rating(request.user)

    return render(request, 'knowledge/article_detail.html', {
        'article': article,
        'related': related,
        'user_rating': user_rating,
        'average_rating': article.average_rating(),
        'rating_count': article.rating_count(),
    })


@login_required
def rate_article(request, slug):
    """Rate an article (AJAX endpoint)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    article = get_object_or_404(Article, slug=slug, is_published=True)
    
    try:
        score = int(request.POST.get('score', 0))
        if score < 1 or score > 5:
            return JsonResponse({'error': 'Score must be 1-5'}, status=400)
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Invalid score'}, status=400)

    # Create or update rating
    rating, created = ArticleRating.objects.update_or_create(
        article=article,
        user=request.user,
        defaults={'score': score}
    )

    return JsonResponse({
        'success': True,
        'score': score,
        'average': article.average_rating(),
        'count': article.rating_count(),
        'created': created,
    })


def knowledge_search(request):
    """Search articles"""
    query = request.GET.get('q', '').strip()
    results = []

    if query:
        results = Article.objects.filter(
            Q(title__icontains=query) |
            Q(summary__icontains=query) |
            Q(content__icontains=query),
            is_published=True
        ).distinct()

    return render(request, 'knowledge/search.html', {
        'query': query,
        'results': results,
    })


# ============================================
# ADMIN ARTICLE MANAGEMENT
# ============================================

@staff_member_required
def admin_article_list(request):
    """List all articles for admin"""
    articles = Article.objects.all().order_by('-created_at')
    
    return render(request, 'knowledge/admin/article_list.html', {
        'articles': articles,
    })


@staff_member_required
def admin_create_article(request):
    """Admin page to create articles"""
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            
            # Set author based on author_type
            author_type = form.cleaned_data.get('author_type')
            if author_type == 'self':
                article.author = request.user
                article.external_author = ''
                article.source_name = ''
                article.source_url = ''
            else:
                article.author = None
            
            article.save()
            messages.success(request, f'Article "{article.title}" created successfully!')
            return redirect('knowledge:admin_article_list')
    else:
        form = ArticleForm()

    return render(request, 'knowledge/admin/create_article.html', {
        'form': form,
    })


@staff_member_required
def admin_edit_article(request, slug):
    """Admin page to edit articles"""
    article = get_object_or_404(Article, slug=slug)
    
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            article = form.save(commit=False)
            
            # Set author based on author_type
            author_type = form.cleaned_data.get('author_type')
            if author_type == 'self':
                article.author = request.user
                article.external_author = ''
                article.source_name = ''
                article.source_url = ''
            else:
                article.author = None
            
            article.save()
            messages.success(request, f'Article "{article.title}" updated successfully!')
            return redirect('knowledge:admin_article_list')
    else:
        # Determine initial author_type
        initial_author_type = 'external' if article.external_author else 'self'
        form = ArticleForm(instance=article, initial={'author_type': initial_author_type})

    return render(request, 'knowledge/admin/edit_article.html', {
        'form': form,
        'article': article,
    })


@staff_member_required
def admin_delete_article(request, slug):
    """Admin page to delete articles"""
    article = get_object_or_404(Article, slug=slug)
    
    if request.method == 'POST':
        title = article.title
        article.delete()
        messages.success(request, f'Article "{title}" deleted.')
        return redirect('knowledge:admin_article_list')

    return render(request, 'knowledge/admin/delete_article.html', {
        'article': article,
    })