from langchain_ollama import ChatOllama, OllamaLLM

llm = OllamaLLM(
    model="llama3.2",
    base_url="https://4e68-115-241-193-70.ngrok-free.app",
    temperature=0,
)

from langchain_core.messages import AIMessage
import json
import uuid

def generate_mcqs(topic, num_questions=5, quiz_head_id="default_quiz_head"):
    prompt = f"""
    Generate {num_questions} multiple-choice questions (MCQs) on the topic: "{topic}".
    ### **Instructions:**
    - Generate exactly **{num_questions}** MCQs based on the provided content.
    - Each MCQ should be **clear, well-structured, and non-repetitive**.
    - Ensure that questions **test understanding**, not just recall.
    - Provide **four answer choices** (`option_1` to `option_4`), making them **plausible yet distinct**.
    - Ensure **one correct answer**, marked as `correct_option` (1, 2, 3, or 4).
    - **Vary the difficulty level**: Include a mix of **basic, intermediate, and advanced** questions.
    - **Avoid ambiguity**: Each question must have only **one clearly correct answer**.
    - **Return only JSON—no explanations, no extra text.**
    Provide the output strictly in JSON format with the following structure:

    [
      {{
        "id": "<unique_question_id>",
        "quiz_head_id": "{quiz_head_id}",
        "question": "<Generated MCQ Question>",
        "option_1": "<First Option>",
        "option_2": "<Second Option>",
        "option_3": "<Third Option>",
        "option_4": "<Fourth Option>",
        "correct_option": "<Correct Option Number (1/2/3/4)>"
      }},
      ...
    ]
    Ensure that the questions are diverse and relevant to the topic. No need to include anything other than the question and options. Give me only the JSON.
    """
    
    response = llm.invoke(prompt)

    try:
        # Attempt to parse the response as JSON
        mcqs = json.loads(response)
    except json.JSONDecodeError:
        print(response)
        return None

    # Assign unique IDs
    for mcq in mcqs:
        mcq["id"] = str(uuid.uuid4())

    return mcqs

# Example Usage
topic = "Machine Learning"
num_questions = 3
quiz_head_id = "ml_quiz_001"

mcqs = generate_mcqs(topic, num_questions, quiz_head_id)

if mcqs:
    print(json.dumps(mcqs, indent=2))