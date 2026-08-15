from flask import Flask, request, jsonify

app = Flask(__name__)

VIP_CONTACTS = ['Yasir', 'Francis', 'yasir', 'francis']


@app.route('/process', methods=['POST'])
def process_message():
    data = request.json or {}

    sender = data.get('sender', '').strip()
    message = data.get('message', '').strip()

    is_vip = any(vip.lower() in sender.lower() for vip in VIP_CONTACTS)
    msg_lower = message.lower()

    # Categorize message
    if any(word in msg_lower for word in [
        'buy', 'sell', 'trade', 'sl', 'tp', 'lot', 'us100', 'signal'
    ]):
        category = 'trading'

    elif any(word in msg_lower for word in [
        'mentor', 'program', 'course', 'invest', 'account',
        'prop', 'price', 'cost', 'how much'
    ]):
        category = 'inquiry'

    elif any(word in msg_lower for word in [
        'personal', 'birthday', 'family', 'health', 'private', 'friend'
    ]):
        category = 'personal'

    elif any(word in msg_lower for word in [
        'hi', 'hey', 'howdy', 'hello', 'what up'
    ]) and len(message) < 40:
        category = 'greeting'

    else:
        category = 'inquiry'

    # Generate reply
    should_flag = False

    if is_vip:
        should_flag = True
        reply = f'Hey {sender}, got your message. I\'ll get back to you shortly.'

    elif category == 'personal':
        should_flag = True
        reply = 'Thanks for this. I\'ll get back to you on this one.'

    elif category == 'greeting':
        reply = 'Howdy man, what\'s up, what brings you here?'

    elif category == 'inquiry':
        reply = 'What exactly do you need? Are you looking for mentorship, a prop firm account, or something else?'

    else:
        reply = 'Alright, let me understand better. What are you looking to do?'

    return jsonify({
        'sender': sender,
        'message': message,
        'category': category,
        'is_vip': is_vip,
        'reply': reply,
        'should_flag': should_flag
    })


@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'status': 'online',
        'message': 'WhatsApp agent API is running'
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
