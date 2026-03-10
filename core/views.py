"""Core views"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from datetime import timedelta
from collections import defaultdict
import json

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

    # Users by province (for pie chart)
    users_by_province = list(
        CustomUser.objects.filter(province__isnull=False)
        .exclude(province='')
        .values('province')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    # Users by language (for pie chart)
    users_by_language = list(
        CustomUser.objects.values('preferred_language')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    # Language labels mapping
    language_labels = {'en': 'English', 'sn': 'Shona', 'nd': 'Ndebele'}
    for item in users_by_language:
        item['label'] = language_labels.get(item['preferred_language'], item['preferred_language'])

    # Recent users
    recent_users = CustomUser.objects.order_by('-date_joined')[:10]

    # User signups per day (last 30 days) - for line chart
    signups_by_day = (
        CustomUser.objects.filter(date_joined__gte=last_30_days)
        .annotate(date=TruncDate('date_joined'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )

    # Fill in missing days with 0
    signup_data = defaultdict(int)
    for item in signups_by_day:
        signup_data[item['date'].strftime('%Y-%m-%d')] = item['count']

    signup_labels = []
    signup_values = []
    for i in range(30, -1, -1):
        date = (now - timedelta(days=i)).date()
        date_str = date.strftime('%Y-%m-%d')
        signup_labels.append(date.strftime('%d %b'))
        signup_values.append(signup_data.get(date_str, 0))

    # --- Forum Stats ---
    total_posts = Post.objects.count()
    total_comments = Comment.objects.count()
    posts_7d = Post.objects.filter(created_at__gte=last_7_days).count()
    comments_7d = Comment.objects.filter(created_at__gte=last_7_days).count()

    # Posts per category (for bar chart)
    posts_by_category = list(
        Category.objects.annotate(post_count=Count('posts'))
        .filter(post_count__gt=0)
        .values('name', 'post_count')
        .order_by('-post_count')[:8]
    )

    # Forum activity by day (last 14 days)
    forum_activity_posts = (
        Post.objects.filter(created_at__gte=now - timedelta(days=14))
        .annotate(date=TruncDate('created_at'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )

    forum_activity_comments = (
        Comment.objects.filter(created_at__gte=now - timedelta(days=14))
        .annotate(date=TruncDate('created_at'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )

    post_data = defaultdict(int)
    comment_data = defaultdict(int)
    for item in forum_activity_posts:
        post_data[item['date'].strftime('%Y-%m-%d')] = item['count']
    for item in forum_activity_comments:
        comment_data[item['date'].strftime('%Y-%m-%d')] = item['count']

    activity_labels = []
    activity_posts = []
    activity_comments = []
    for i in range(14, -1, -1):
        date = (now - timedelta(days=i)).date()
        date_str = date.strftime('%Y-%m-%d')
        activity_labels.append(date.strftime('%d %b'))
        activity_posts.append(post_data.get(date_str, 0))
        activity_comments.append(comment_data.get(date_str, 0))

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

    # Chat activity by day (last 14 days)
    chat_by_day = (
        Message.objects.filter(created_at__gte=now - timedelta(days=14))
        .annotate(date=TruncDate('created_at'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )

    chat_data = defaultdict(int)
    for item in chat_by_day:
        chat_data[item['date'].strftime('%Y-%m-%d')] = item['count']

    chat_labels = []
    chat_values = []
    for i in range(14, -1, -1):
        date = (now - timedelta(days=i)).date()
        date_str = date.strftime('%Y-%m-%d')
        chat_labels.append(date.strftime('%d %b'))
        chat_values.append(chat_data.get(date_str, 0))

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
    approved_agritex_count = CustomUser.objects.filter(agritex_verification_status='approved').count()

    context = {
        # User stats
        'total_users': total_users,
        'new_users_7d': new_users_7d,
        'new_users_30d': new_users_30d,
        'active_users_7d': active_users_7d,
        'users_by_province': users_by_province,
        'users_by_language': users_by_language,
        'recent_users': recent_users,

        # Chart data - User signups
        'signup_labels': json.dumps(signup_labels),
        'signup_values': json.dumps(signup_values),

        # Forum stats
        'total_posts': total_posts,
        'total_comments': total_comments,
        'posts_7d': posts_7d,
        'comments_7d': comments_7d,
        'active_categories': active_categories,
        'recent_posts': recent_posts,
        'active_posters': active_posters,
        'posts_by_category': posts_by_category,

        # Chart data - Forum activity
        'activity_labels': json.dumps(activity_labels),
        'activity_posts': json.dumps(activity_posts),
        'activity_comments': json.dumps(activity_comments),

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

        # Chart data - Chat activity
        'chat_labels': json.dumps(chat_labels),
        'chat_values': json.dumps(chat_values),

        # Chart data - Province distribution
        'province_labels': json.dumps([p['province'].replace('_', ' ').title() for p in users_by_province]),
        'province_values': json.dumps([p['count'] for p in users_by_province]),

        # Chart data - Language distribution
        'language_labels': json.dumps([l['label'] for l in users_by_language]),
        'language_values': json.dumps([l['count'] for l in users_by_language]),

        # AGRITEX stats
        'pending_agritex_count': pending_agritex_count,
        'approved_agritex_count': approved_agritex_count,
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