const generateBtn = document.getElementById("generateBtn");
const clearBtn = document.getElementById("clearBtn");
const extractBtn = document.getElementById("extractBtn");
const textInput = document.getElementById("textInput");
const numCardsInput = document.getElementById("numCards");
const difficultySelect = document.getElementById("difficulty");
const statusEl = document.getElementById("status");
const cardsContainer = document.getElementById("cardsContainer");
const countLabel = document.getElementById("countLabel");
const fileInput = document.getElementById("fileInput");

let extractedText = "";

function createFlashcard(question, answer, i) {
  const card = document.createElement("div");
  card.className = "flashcard";

  card.innerHTML = `
    <h3>Q${i + 1}. ${question}</h3>
    <p><strong>Answer:</strong> ${answer}</p>
    <small>Auto-generated using simple NLP demo</small>
  `;
  return card;
}

function renderCards(cards) {
  cardsContainer.innerHTML = "";
  cards.forEach((card, i) => {
    const el = createFlashcard(card.question, card.answer, i);
    cardsContainer.appendChild(el);
  });
  countLabel.textContent = cards.length + " cards";
}

async function extractTextFromFile() {
  const file = fileInput.files[0];
  if (!file) {
    statusEl.textContent = "Please choose a file first.";
    return;
  }
  const formData = new FormData();
  formData.append("file", file);
  statusEl.textContent = "Uploading and extracting text...";

  try {
    const res = await fetch("/api/upload", {
      method: "POST",
      body: formData,
    });

    if (!res.ok) {
      throw new Error("Upload failed");
    }

    const data = await res.json();
    extractedText = data.text || "";
    if (extractedText) {
      textInput.value = extractedText;
      statusEl.textContent = "Text extracted from file successfully.";
    } else {
      statusEl.textContent = "Could not extract text from this file.";
    }
  } catch (err) {
    console.error(err);
    statusEl.textContent = "Error extracting text from file.";
  }
}

async function generateFlashcards() {
  const rawText = textInput.value.trim() || extractedText.trim();
  const numCards = parseInt(numCardsInput.value) || 5;
  const difficulty = difficultySelect.value;

  if (!rawText) {
    statusEl.textContent = "Please paste text or extract from a file first.";
    return;
  }

  statusEl.textContent = "Generating flashcards on the server...";

  try {
    const res = await fetch("/api/generate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        text: rawText,
        difficulty,
        numCards,
      }),
    });

    if (!res.ok) {
      throw new Error("Generation failed");
    }

    const data = await res.json();
    renderCards(data.cards || []);
    statusEl.textContent = "Flashcards generated successfully.";
  } catch (err) {
    console.error(err);
    statusEl.textContent = "Error generating flashcards.";
  }
}

generateBtn.addEventListener("click", generateFlashcards);
extractBtn.addEventListener("click", extractTextFromFile);

clearBtn.addEventListener("click", () => {
  textInput.value = "";
  fileInput.value = "";
  extractedText = "";
  cardsContainer.innerHTML = "";
  countLabel.textContent = "0 cards";
  statusEl.textContent = "";
});
