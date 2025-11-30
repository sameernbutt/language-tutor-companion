from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List, Union
import requests
import random
import json
import re
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Groq API configuration (free tier with generous limits)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_NAME = "llama-3.1-8b-instant"  # Free, fast, and powerful

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    text: str
    language: str = "spanish"
    level: str = "novice"
    is_exercise: bool = False
    enable_feedback: bool = False  # Default OFF for conversation mode
    context: List[str] = []  # Track conversation history
    target_answers: Optional[List[str]] = []
    start_conversation: bool = False  # NEW: To initiate a conversation 
class ExerciseSubmission(BaseModel):
    user_answer: str
    exercise_type: str
    target_answer: str
    language: str
    level: str

class ProgressData(BaseModel):
    user_id: str
    date: str
    score: int
    language: str
    level: str
    exercise_type: Optional[str] = None

progress_db = []

def load_vocab(language: str, level: str) -> List[str]:
    try:
        with open(f"./data/vocab_by_level.json", "r", encoding="utf-8") as f:
            vocab = json.load(f)
        return vocab.get(language, {}).get(level, [])
    except Exception as e:
        print(f"Error loading vocab: {e}")
        return []

def get_cefr(level):
    if level == "beginner":
        cefr = "A1, A2, or B1"
    elif level == "novice":
        cefr = "A1"
    elif level == "intermediate":
        cefr = "A1, A2, B1, B2, or C1"
    return cefr

    


def get_prompt_file(message: Message) -> str:
    suffix = "tutor" if message.is_exercise else "converser"
    return f"./prompts/{message.language}_{suffix}.txt"


def generate_tutor_response(system_prompt: str, user_text: str, language: str,
                          level: str, is_exercise: bool, 
                          vocab_limit: Optional[List[str]] = None,
                          context: List[str] = None) -> str:
    
    # Build context-aware prompt
    context_str = "\n".join([
    f"User: {msg}" if i % 2 == 0 else f"Tutor: {msg}"
    for i, msg in enumerate(context[-6:])
    ]) if context else ""

    cefr = get_cefr(level)

    # get greeting to make sure model doesnt say the same thing or greeting over and over again
    greetings = {
    "spanish": "hola",
    "urdu": "salaam",
    "french": "bonjour",
    "finnish": "hei",
    "italian": "ciao",
    "german": "hallo",
    "indonesian": "halo",
    "swahili": "hujambo",
    "icelandic": "halló"
    }
    greeting = greetings[language.lower()]


    
    prompt = f"""
        You are a friendly {language} tutor helping a student practice casual conversation.
        This is a continuous chat. Do NOT repeat greetings like "{greeting}" every time. 
        Instead, build naturally on the previous messages. Ask follow-up questions.
        Use informal {language} and sound like a native speaker.

        The user is {level} level. Respond accordingly.'

        Use only words of {cefr} CEFR level.

        Here is the conversation so far:
        {context_str}
        User just said: {user_text}

        Your turn:
        """



    if is_exercise:
        prompt += (
            "\nAdditional exercise feedback requirements:\n"
            "- Clearly indicate correct/incorrect\n"
            "- Explain solution if needed\n"
            "- Suggest similar practice\n"
        )
    elif vocab_limit:
        prompt += (
            f"\nIMPORTANT: Only use the following words in your reply (unless absolutely necessary):\n"
            f"{', '.join(vocab_limit)}\n"
            "Make sure the response is understandable and natural with these words."
        )
    print(prompt)
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        response = requests.post(
            GROQ_API_URL,
            headers=headers,
            json={
                "model": MODEL_NAME,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 512,
                "temperature": 0.7
            },
            timeout=60
        )
        response.raise_for_status()
        chat_response = response.json()["choices"][0]["message"]["content"]
        print(chat_response)
        print("\nNew one is:\n")
        if "(Note" in chat_response:
            chat_response_copy = chat_response
            chat_response = ""
            for char in chat_response_copy:
                if char == "(":
                    break
                chat_response = chat_response + char
        print(chat_response)
        return chat_response
    except Exception as e:
        print(f"API Error: {e}")
        return "I appreciate your effort! Let's keep practicing."


@app.post("/chat")
async def chat_with_tutor(message: Message):
    # Handle conversation initiation
    if message.start_conversation:
        prompt_file = get_prompt_file(message)
        with open(prompt_file, "r", encoding="utf-8") as f:
            system_prompt = f.read()
        
        # Generate an opening greeting and question
        opening_prompt = f"""You are starting a new conversation with a {message.level} level {message.language} student. 
        Greet them warmly and ask an engaging introductory question in {message.language}.
        Keep it simple and appropriate for their level.
        Do not use English. Only respond in {message.language}."""
        
        tutor_response = generate_tutor_response(
            system_prompt,
            opening_prompt,
            message.language,
            message.level,
            False,
            None,
            []
        )
        
        return {"response": tutor_response}
    
    # If user is answering an exercise with expected answers
    if message.is_exercise and message.target_answers:
        user_input = message.text.strip().lower()
        correct_answers = [a.strip().lower() for a in message.target_answers]
        print(correct_answers)

        if user_input in correct_answers:
            return {
                "response": "✅ Correct! You're doing great!",
                "feedback": {
                    "is_correct": True,
                    "correct_answers": correct_answers
                }
            }
        else:
            answerStr = ""
            if len(correct_answers) == 1:
                answerStr = correct_answers[0] + "."
            elif len(correct_answers) == 2:
                answerStr = f"{correct_answers[0]} and {correct_answers[1]}."
            else:
                all_but_last = ", ".join(correct_answers[:-1])
                answerStr = f"{all_but_last}, and {correct_answers[-1]}."
            response = "❌ Not quite. Correct answers include: " + answerStr

            return {
                "response": response,
                "feedback": {
                    "is_correct": False,
                    "correct_answers": correct_answers
                }
            }
    elif message.is_exercise:
        return {
            "response": "I have been programmed to not engage in conversation while in Exercise Mode. Please select \"Get Exercise\" to generate an exercise."
        }

    # Regular conversation mode
    prompt_file = get_prompt_file(message)
    with open(prompt_file, "r", encoding="utf-8") as f:
        system_prompt = f.read()

    if "¿correcto?" in message.text.lower() or "¿está bien?" in message.text.lower():
        message.enable_feedback = True

    vocab_limit = None
    if message.level != "advanced" and not message.is_exercise:
        vocab_limit = load_vocab(message.language, message.level)

    tutor_response = generate_tutor_response(
        system_prompt,
        message.text,
        message.language,
        message.level,
        message.is_exercise,
        vocab_limit,
        message.context
    )

    return {
        "response": tutor_response,
    }



class VocabExerciseRequest(BaseModel):
    language: str
    level: str

@app.post("/vocab-exercise")
async def generate_vocab_exercise(request: VocabExerciseRequest):
    language = request.language
    level = request.level
    
    if level == "novice":
        exercise_types = ["TRANSLATION"]
    elif level == "beginner":
        exercise_types = ["TRANSLATION", "MULTIPLE_CHOICE"]
    elif level == "intermediate":
        exercise_types = ["CONJUGATION", "TRANSLATION"]
    else:
        exercise_types = ["TRANSLATION"]
        
    exercise_type = random.choice(exercise_types)
    cefr = get_cefr(level)
    
    # Build JSON-oriented prompt
    if exercise_type == "TRANSLATION":
        prompt = f"""Generate a vocabulary translation exercise for a {level} level {language} student.

Provide your response in VALID JSON format with these exact fields:
{{
  "type": "TRANSLATION",
  "instructions": "Translate the following word to {language}",
  "content": "[English word]",
  "target": ["[{language} translation]"]
}}

The English word should be appropriate for CEFR level {cefr}.
Make sure to use proper JSON formatting with double quotes."""

    elif exercise_type == "MULTIPLE_CHOICE":
        prompt = f"""Generate a multiple choice vocabulary exercise for a {level} level {language} student.

Provide your response in VALID JSON format with these exact fields:
{{
  "type": "MULTIPLE_CHOICE",
  "instructions": "Choose the correct English translation",
  "content": "What does '[{language} word]' mean?\\nA) [option1]\\nB) [option2]\\nC) [option3]",
  "target": ["A"]
}}

The {language} word should be appropriate for CEFR level {cefr}.
Make one of the options the correct answer and note which letter (A/B/C) it is in the target field.
Make sure to use proper JSON formatting with double quotes."""

    elif exercise_type == "CONJUGATION":
        prompt = f"""Generate a verb conjugation exercise for a {level} level {language} student.

Provide your response in VALID JSON format with these exact fields:
{{
  "type": "CONJUGATION",
  "instructions": "Conjugate the verb in the specified tense",
  "content": "Conjugate '[{language} verb]' in [tense/form]",
  "target": ["[correct conjugation]"]
}}

The verb should be appropriate for CEFR level {cefr}.
Make sure to use proper JSON formatting with double quotes."""

    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        response = requests.post(
            GROQ_API_URL,
            headers=headers,
            json={
                "model": MODEL_NAME,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 512,
                "temperature": 0.7,
                "response_format": {"type": "json_object"}
            },
            timeout=60
        )
        response.raise_for_status()
        
        content = response.json()["choices"][0]["message"]["content"]
        exercise_data = json.loads(content)
        
        return {
            "type": exercise_data.get("type", exercise_type),
            "instructions": exercise_data.get("instructions", ""),
            "content": exercise_data.get("content", ""),
            "target": exercise_data.get("target", []),
            "raw": content
        }
    except Exception as e:
        print(f"Error generating exercise: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/grade-exercise")
async def grade_exercise(submission: ExerciseSubmission):
    is_correct = submission.user_answer.lower().strip() == submission.target_answer.lower().strip() or submission.target_answer.lower().strip()[0].lower() == submission.user_answer.lower().strip()[0].lower()
    
    if is_correct:
        feedback = "¡Correcto! 🎉" if submission.language == "spanish" else "Bilkul durust! 🎉"
        score = 100
    else:
        feedback = f"Almost! The correct answer was: {submission.target_answer}"
        score = 50
    
    return {
        "is_correct": is_correct,
        "feedback": feedback,
        "score": score,
        "target_answer": submission.target_answer
    }

@app.post("/record-progress")
async def record_progress(data: ProgressData):
    progress_db.append(data.dict())
    return {"status": "success"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
