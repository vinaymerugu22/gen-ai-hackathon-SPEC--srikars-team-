from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# This opens your website
@app.route("/")
def home():
    return render_template("index.html")

# This handles AI questions
@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    question = data["question"]

    # Simple backend logic
    answer = "I am your AI tutor. Ask about Machine Learning."

    if "ai" in question.lower():
        answer = "AI means Artificial Intelligence."
    elif "ml" in question.lower():
        answer = "Machine Learning is part of AI."

    return jsonify({"answer": answer})

# Start server
if __name__ == "__main__":
    app.run(debug=True)
