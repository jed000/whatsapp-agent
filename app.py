import os
from flask import Flask, request, jsonify
from openai import OpenAI

app = Flask(__name__)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

VIP_CONTACTS = ["Yasir", "Francis", "yasir", "francis"]

SYSTEM_PROMPT = """
You are Jed's WhatsApp assistant.

Your job is to help people who message jed about:
- Trading
- Trading mentorship
- Prop firm accounts
- Investment-related enquiries
- Other services Laktrade offers

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
- If you don't know something, say that jed will clarify it.
- Don't aggressively sell.
- Understand what the person actually wants before trying to qualify them.

LEAD QUALIFICATION:
Treat someone as a serious prospect when they clearly indicate that they:
- want to join the mentorship,
- are ready to pay,
- want to start,
- want payment details,
- want to book/register,
- or explicitly ask to speak with Laktrade.

When someone becomes a serious prospect, tell them that jed will take over the conversation.

VIP CONTACTS:
VIP contacts should receive priority and should be flagged for jed.

Your response should ONLY contain the message that should be sent to the customer.
Do not explain your reasoning.
"""

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "online",
        "message": "jed AI agent is running"
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

    # Add previous conversation
    for item in history:
        role = item.get("role")
        content = item.get("content")

        if role in ["user", "assistant"] and content:
            messages.append({
                "role": role,
                "content": content
            })

    # Add current message
    messages.append({
        "role": "user",
        "content": message
    })

    response = client.responses.create(
        model="gpt-5-mini",
        input=messages
    )

    reply = response.output_text

    # Basic handoff detection
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
        "speak to laktrade",
        "talk to laktrade"
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


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )
