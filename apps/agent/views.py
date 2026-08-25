from django.http import HttpResponseBadRequest
from django.shortcuts import render

from .services import ShoppingAgent


def chat(request):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")
    history = request.session.get("agent_history", [])
    agent = ShoppingAgent(history=history)
    answer = agent.reply(request.POST.get("message", "").strip())
    request.session["agent_history"] = agent.history[-12:]
    return render(
        request,
        "agent/partials/message.html",
        {"user_message": request.POST.get("message", ""), "answer": answer},
    )
