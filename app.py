from flask import Flask, request, jsonify, send_from_directory
import os
import io

# Optional imports for real extraction; if not installed, PDF/DOCX/IMAGE will be skipped gracefully.
try:
    import PyPDF2
except ImportError:  # type: ignore
    PyPDF2 = None

try:
    import docx  # python-docx
except ImportError:  # type: ignore
    docx = None

try:
    from PIL import Image
    import pytesseract
except ImportError:  # type: ignore
    Image = None
    pytesseract = None

app = Flask(__name__, static_folder="static", static_url_path="")

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

def extract_from_pdf(file_storage):
    if PyPDF2 is None:
        return ""
    reader = PyPDF2.PdfReader(file_storage.stream)
    text = []
    for page in reader.pages:
        try:
            text.append(page.extract_text() or "")
        except Exception:
            continue
    return "\n".join(text)

def extract_from_docx(file_storage):
    if docx is None:
        return ""
    data = file_storage.read()
    file_stream = io.BytesIO(data)
    document = docx.Document(file_stream)
    return "\n".join(p.text for p in document.paragraphs)

def extract_from_image(file_storage):
    if Image is None or pytesseract is None:
        return ""
    image = Image.open(file_storage.stream)
    text = pytesseract.image_to_string(image)
    return text

def extract_from_txt(file_storage):
    data = file_storage.read()
    try:
        return data.decode("utf-8", errors="ignore")
    except Exception:
        return ""

@app.route("/api/upload", methods=["POST"])
def upload():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    filename = file.filename.lower()
    text = ""

    try:
        if filename.endswith(".pdf"):
            text = extract_from_pdf(file)
        elif filename.endswith(".docx"):
            text = extract_from_docx(file)
        elif any(filename.endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".bmp", ".tiff"]):
            text = extract_from_image(file)
        elif filename.endswith(".txt"):
            text = extract_from_txt(file)
    except Exception as e:
        print("Error extracting text:", e)
        text = ""

    return jsonify({"text": text})

def simple_nlp_generate(text, difficulty, num_cards):
    cleaned = " ".join(text.split())
    import re
    sentences = re.split(r"(?<=[.?!])\s+", cleaned)
    sentences = [s.strip() for s in sentences if s.strip()]
    if not sentences:
        sentences = [cleaned or "This is an example concept from your notes."]

    cards = []
    for i in range(num_cards):
        base = sentences[i % len(sentences)]
        snippet = base[:120] + ("..." if len(base) > 120 else "")

        if difficulty == "easy":
            question = f"What is the main idea of: \"{snippet}\"?"
        elif difficulty == "hard":
            question = f"Explain in detail the concept described in: \"{snippet}\""
        else:
            question = f"Summarize this line: \"{snippet}\""

        cards.append(
            {
                "question": question,
                "answer": base,
            }
        )
    return cards

@app.route("/api/generate", methods=["POST"])
def generate():
    data = request.get_json(force=True)
    text = data.get("text", "") or ""
    difficulty = data.get("difficulty", "medium")
    num_cards = int(data.get("numCards", 5))

    if not text.strip():
        return jsonify({"cards": []})

    num_cards = max(1, min(30, num_cards))

    cards = simple_nlp_generate(text, difficulty, num_cards)
    return jsonify({"cards": cards})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
