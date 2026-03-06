"""Chatbot views - Chat interface and API"""

import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Conversation, Message
from .ai_service import get_ai_response


@login_required
def chat_home(request):
    """Main chat interface"""
    conversations = Conversation.objects.filter(user=request.user)[:20]

    # Get or create active conversation
    conversation_id = request.GET.get('c')
    active_conversation = None
    messages_list = []

    if conversation_id:
        active_conversation = get_object_or_404(
            Conversation, id=conversation_id, user=request.user
        )
        messages_list = active_conversation.messages.all()

    context = {
        'conversations': conversations,
        'active_conversation': active_conversation,
        'messages': messages_list,
    }
    return render(request, 'chatbot/chat.html', context)


@login_required
@require_POST
def send_message(request):
    """Handle incoming chat messages and return AI response"""
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        conversation_id = data.get('conversation_id')
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({'error': 'Invalid request'}, status=400)

    if not user_message:
        return JsonResponse({'error': 'Empty message'}, status=400)

    # Initialize conversation
    conversation = None

    # Try to get existing conversation
    if conversation_id:
        try:
            conversation = Conversation.objects.get(
                id=conversation_id, user=request.user
            )
        except Conversation.DoesNotExist:
            conversation = None

    # Create new conversation if none exists
    if not conversation:
        title = user_message[:80] + ('...' if len(user_message) > 80 else '')
        conversation = Conversation.objects.create(
            user=request.user,
            title=title
        )

    # Save user message
    Message.objects.create(
        conversation=conversation,
        role='user',
        content=user_message
    )

    # Build conversation history for context
    history = []
    past_messages = conversation.messages.order_by('created_at')
    for msg in past_messages:
        history.append({
            'role': msg.role,
            'content': msg.content
        })

    # Get AI response
    result = get_ai_response(user_message, history)

    # Save assistant response
    Message.objects.create(
        conversation=conversation,
        role='assistant',
        content=result['response']
    )

    # Update conversation timestamp
    conversation.save()

    return JsonResponse({
        'response': result['response'],
        'source': result['source'],
        'conversation_id': conversation.id,
        'conversation_title': conversation.title,
    })


@login_required
def new_conversation(request):
    """Start a fresh conversation"""
    return redirect('chatbot:home')


@login_required
@require_POST
def delete_conversation(request, conversation_id):
    """Delete a conversation"""
    conversation = get_object_or_404(
        Conversation, id=conversation_id, user=request.user
    )
    conversation.delete()
    return redirect('chatbot:home')