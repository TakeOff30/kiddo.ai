# kiddo.ai 🤖📚

Kiddo.ai transforms your exam preparation by challenging you to become a teacher. The core of the experience revolves around **explaining complex concepts to "Kiddo," your virtual study companion, as if he were a curious child.** This process, rooted in the Feynman technique, forces you to simplify and deeply understand the material, truly cementing it in your mind.

But here's the catch: if you don't regularly explain things to Kiddo or help him review, **he starts to "forget" what you've taught him!** This unique dynamic is designed to motivate you, leveraging principles like Loss Aversion. Seeing Kiddo's understanding fade should spur you on to consistently engage, teach, and reinforce – ensuring both you and Kiddo master the concepts together. The system also integrates Spaced Repetition and Active Recall to further enhance learning and retention.

## ✨ Key Features

* **Interactive Learning:** Explain concepts to Kiddo, a curious avatar that wants to learn.
* **Effective Techniques:** Implements Feynman and "Teach Others" methods.
* **Smart Study:** Utilizes Spaced Repetition and Active Recall.
* **Motivation:** Includes gamification elements to maintain high engagement.
* **Source-Based:** Users provide study material (PDF) as a reference.

## 🔧 How it Works

The system is an API-based backend with two main pipelines:

1.  **Ingestion Pipeline:**
    * The user creates a new "exam" by providing the date, study schedule, and the reference PDF.
    * The PDF is chunked and stored in a vector database.
    * An agent identifies macro-areas and key concepts.

2.  **Kiddo Pipeline (Learning Interaction):**
    * The user selects a macro-area.
    * Kiddo initiates a question-driven dialogue for that set of concepts.
    * **Concept Validation:** The user's explanation is compared with the original content.
    * **Knowledge Graph Update:** If the explanation is accurate, the concept is integrated into Kiddo's internal knowledge graph. The graph nodes represent concepts and their learning status:
        * 🟢 **Green:** well-learned and stable.
        * 🟡 **Yellow:** correct but needs review (initial state).
        * 🔴 **Red:** incorrect concept.
        * ⚪ **Gray:** forgotten due to lack of review.

## 🚀 Setup

The application is dockerized. Ensure you have Docker installed.

1.  Create two `.env` files following the template provided in `.env.template`.
2.  Run the application with:
    ```bash
    docker compose up
    ```