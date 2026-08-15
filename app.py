@app.route("/test", methods=["GET"])
def test_ai():
    response = client.responses.create(
        model="gpt-5-mini",
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
        "reply": response.output_text
    })
