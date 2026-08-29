from django.core.cache import cache
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render

from .services import MAX_MESSAGE_LENGTH, ShoppingAgent


def _client_key(request):
    return request.META.get("REMOTE_ADDR", "unknown")


def chat(request):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")
    message = request.POST.get("message", "").strip()
    if not message:
        return HttpResponseBadRequest("Message cannot be empty.")
    if len(message) > MAX_MESSAGE_LENGTH:
        return HttpResponseBadRequest(
            f"Message cannot exceed {MAX_MESSAGE_LENGTH} characters."
        )
    if not cache.add(f"agent-rate:{_client_key(request)}", True, timeout=1):
        return HttpResponse("Please wait before sending another message.", status=429)

    history = request.session.get("agent_history", [])
    agent = ShoppingAgent(history=history)
    try:
        answer = agent.reply(message)
    except (ConnectionError, TimeoutError, OSError):
        return HttpResponse("The assistant is temporarily unavailable.", status=503)
    except Exception:
        return HttpResponse("The assistant could not process that request.", status=503)
    request.session["agent_history"] = agent.history[-12:]
    return render(
        request,
        "agent/partials/message.html",
        {"user_message": message, "answer": answer},
    )
