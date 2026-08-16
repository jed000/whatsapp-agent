import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)


VIP_CONTACTS = ["Yasir", "Francis", "yasir", "francis"]

SYSTEM_PROMPT = """
You are Jed's Capital's WhatsApp assistant.

Your job is to help people who message Jed's Capital about trading,
trading mentorship, prop firm accounts, investment-related enquiries,
and other services Jed's Capital offers.

CONVERSATION STYLE:
- Be natural, warm and conversational.
- Keep replies concise because this is WhatsApp.
- Do not sound like a corporate chatbot.
- Understand Nigerian English and casual expressions.
- Ask one useful question at a time.
- Remember information already provided in the conversation.
- Never repeatedly ask something the person has already answered.

IMPORTANT RULES:
- Never invent prices, services, guarantees, profits, testimonials or facts.
- Never guarantee investment or trading returns.
- Do not give personalised financial advice.
- If you don't know something, say that Jed will clarify it.
- Don't aggressively sell.
- Understand what the person actually wants before trying to qualify them.

LEAD QUALIFICATION:
Treat someone as a serious prospect when they clearly indicate that they:
- want to join the mentorship,
- are ready to pay,
- want to start,
- want payment details,
- want to register,
- or explicitly ask to speak with Jed.

When someone becomes a serious prospect, tell them that Jed will take over the conversation.

VIP CONTACTS:
VIP contacts should receive priority and should be flagged for Jed.

Your response should ONLY contain the message that should be sent
to the customer. Do not explain your reasoning.
"""


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "online",
        "message": "Jed's Capital AI agent is running"
    })


@app.route("/process", methods=["POST"])
def process_message():

    data = request.json or {}

    sender = data.get("sender", "").strip()
    message = data.get("message", "").strip()
    history = data.get("history", [])

    is_vip = any(
        vip.lower() in sender.lower()
        for vip in VIP_CONTACTS
    )

    messages = [
        {
            "role": "developer",
            "content": SYSTEM_PROMPT
        }
    ]

    for item in history:
        role = item.get("role")
        content = item.get("content")

        if role in ["user", "assistant"] and content:
            messages.append({
                "role": role,
                "content": content
            })

    messages.append({
        "role": "user",
        "content": message
    })

    response = client.responses.create(
        model="openrouter/free",
        input=messages
    )

    reply = response.output_text

    handoff_words = [
        "ready to join",
        "ready to start",
        "how do i pay",
        "payment details",
        "payment",
        "register",
        "registration",
        "sign up",
        "book",
        "speak to jed",
        "talk to jed"
    ]

    should_flag = (
        is_vip or
        any(word in message.lower() for word in handoff_words)
    )

    return jsonify({
        "sender": sender,
        "message": message,
        "reply": reply,
        "is_vip": is_vip,
        "should_flag": should_flag
    })


@app.route("/test", methods=["GET"])
def test_ai():

    try:
        response = client.responses.create(
            model="openrouter/free",
            input=[
                {
                    "role": "developer",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": "Hey, I'm interested in your mentorship"
                }
            ]
        )

        return jsonify({
            "status": "success",
            "reply": response.output_text
        })

    except Exception as e:

        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )
