"""Core views"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.db.models import Count, Q
from datetime import timedelta

from django.contrib import messages

from accounts.models import CustomUser
from forum.models import Post, Comment, Category
from knowledge.models import Article, ArticleRating
from chatbot.models import Conversation, Message


def home(request):
    """Homepage"""
    return render(request, 'core/home.html')


def about(request):
    """About page"""
    return render(request, 'core/about.html')


@staff_member_required
def admin_dashboard(request):
    """Admin dashboard with site analytics"""

    now = timezone.now()
    today = now.date()
    last_7_days = now - timedelta(days=7)
    last_30_days = now - timedelta(days=30)

    # --- User Stats ---
    total_users = CustomUser.objects.count()
    new_users_7d = CustomUser.objects.filter(date_joined__gte=last_7_days).count()
    new_users_30d = CustomUser.objects.filter(date_joined__gte=last_30_days).count()
    active_users_7d = CustomUser.objects.filter(last_login__gte=last_7_days).count()

    # Users by province
    users_by_province = (
        CustomUser.objects.filter(province__isnull=False)
        .exclude(province='')
        .values('province')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    # Users by language
    users_by_language = (
        CustomUser.objects.values('preferred_language')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    # Recent users
    recent_users = CustomUser.objects.order_by('-date_joined')[:10]

    # --- Forum Stats ---
    total_posts = Post.objects.count()
    total_comments = Comment.objects.count()
    posts_7d = Post.objects.filter(created_at__gte=last_7_days).count()
    comments_7d = Comment.objects.filter(created_at__gte=last_7_days).count()

    # Most active forum categories
    active_categories = (
        Category.objects.annotate(
            post_count=Count('posts'),
            recent_posts=Count('posts', filter=Q(posts__created_at__gte=last_7_days))
        )
        .order_by('-post_count')
    )

    # Recent posts
    recent_posts = Post.objects.select_related('author', 'category').order_by('-created_at')[:10]

    # Most active users (by posts + comments)
    active_posters = (
        CustomUser.objects.annotate(
            post_count=Count('forum_posts'),
            comment_count=Count('forum_comments')
        )
        .order_by('-post_count')[:10]
    )

    # --- Knowledge Stats ---
    total_articles = Article.objects.count()
    published_articles = Article.objects.filter(is_published=True).count()
    total_ratings = ArticleRating.objects.count()

    # Most viewed articles
    popular_articles = Article.objects.filter(is_published=True).order_by('-views')[:10]

    # Recent ratings
    recent_ratings = (
        ArticleRating.objects.select_related('article', 'user')
        .order_by('-created_at')[:10]
    )

    # --- Chatbot Stats ---
    total_conversations = Conversation.objects.count()
    total_messages = Message.objects.count()
    conversations_7d = Conversation.objects.filter(created_at__gte=last_7_days).count()
    messages_7d = Message.objects.filter(created_at__gte=last_7_days).count()

    # Most active chatbot users
    active_chatters = (
        CustomUser.objects.annotate(
            convo_count=Count('conversations'),
            msg_count=Count('conversations__messages')
        )
        .filter(convo_count__gt=0)
        .order_by('-convo_count')[:10]
    )

    # Recent conversations
    recent_conversations = (
        Conversation.objects.select_related('user')
        .order_by('-updated_at')[:10]
    )

    # --- AGRITEX Stats ---
    pending_agritex_count = CustomUser.objects.filter(agritex_verification_status='pending').count()

    context = {
        # User stats
        'total_users': total_users,
        'new_users_7d': new_users_7d,
        'new_users_30d': new_users_30d,
        'active_users_7d': active_users_7d,
        'users_by_province': users_by_province,
        'users_by_language': users_by_language,
        'recent_users': recent_users,

        # Forum stats
        'total_posts': total_posts,
        'total_comments': total_comments,
        'posts_7d': posts_7d,
        'comments_7d': comments_7d,
        'active_categories': active_categories,
        'recent_posts': recent_posts,
        'active_posters': active_posters,

        # Knowledge stats
        'total_articles': total_articles,
        'published_articles': published_articles,
        'total_ratings': total_ratings,
        'popular_articles': popular_articles,
        'recent_ratings': recent_ratings,

        # Chatbot stats
        'total_conversations': total_conversations,
        'total_messages': total_messages,
        'conversations_7d': conversations_7d,
        'messages_7d': messages_7d,
        'active_chatters': active_chatters,
        'recent_conversations': recent_conversations,

        # AGRITEX stats
        'pending_agritex_count': pending_agritex_count,
    }

    return render(request, 'core/dashboard.html', context)


@staff_member_required
def agritex_applications(request):
    """View all AGRITEX applications"""
    pending = CustomUser.objects.filter(agritex_verification_status='pending').order_by('-agritex_applied_at')
    approved = CustomUser.objects.filter(agritex_verification_status='approved').order_by('-agritex_verified_at')[:10]
    rejected = CustomUser.objects.filter(agritex_verification_status='rejected').order_by('-id')[:10]

    return render(request, 'core/agritex_applications.html', {
        'pending': pending,
        'approved': approved,
        'rejected': rejected,
    })


@staff_member_required
def agritex_review(request, user_id):
    """Review a single AGRITEX application"""
    applicant = get_object_or_404(CustomUser, id=user_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        notes = request.POST.get('notes', '')

        if action == 'approve':
            applicant.is_agritex_officer = True
            applicant.agritex_verification_status = 'approved'
            applicant.agritex_verified_at = timezone.now()
            applicant.agritex_verification_notes = notes
            applicant.save()
            messages.success(request, f'{applicant.username} has been approved as an AGRITEX officer.')

        elif action == 'reject':
            applicant.is_agritex_officer = False
            applicant.agritex_verification_status = 'rejected'
            applicant.agritex_verification_notes = notes
            applicant.save()
            messages.warning(request, f'{applicant.username} application has been rejected.')

        return redirect('core:agritex_applications')

    return render(request, 'core/agritex_review.html', {
        'applicant': applicant,
    })