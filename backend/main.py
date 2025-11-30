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

app = FastAPI()

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
practiced_words = []
practiced_translated = []
practiced_mc = []

OLLAMA_URL = "http://localhost:11434/api/generate"

def load_vocab(language: str, level: str) -> List[str]:
    try:
        with open(f"./data/vocab_by_level.json", "r") as f:
            vocab = json.load(f)
        return vocab.get(language, {}).get(level, [])
    except Exception as e:
        print(f"Error loading vocab: {e}")
        return []

practiced_mc = [] 

# flags true if somethings wrong, otherwise false
def check_mc(given_parts, correct_word):
    target_str = given_parts["target"][0]  # Take first element 
    print("target str is " + str(target_str))
    target_letter = target_str.rstrip(')')  # Remove ")" if present
    print("Target letter is " + str(target_letter))

    input_string = given_parts["content"]
    words = input_string.split(" ")
    print("Input string is " + str(input_string))
    
    found_word = None
    for i in range(len(words)):
        if words[i] == f"{target_letter})":
            if i + 1 < len(words):
                found_word = words[i + 1]
                break  # Exit the loop once the word is found
    
    print("\nWords are:")
    print(found_word)
    print(correct_word)
    print()
    found_word = found_word.lower()
    correct_word = correct_word.lower()
    if found_word in practiced_mc:
        return True # word already been practiced so flag
    elif not found_word == correct_word:
        return True # word doesnt match correct answer
    else:
        practiced_mc.append(found_word) # if we good then just keep track of it
        return False

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
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False,
                "system": system_prompt
            },
            timeout=30
        )
        response.raise_for_status()
        chat_response = response.json()["response"]
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
    except Exception:
        return "I appreciate your effort! Let's keep practicing."


@app.post("/chat")
async def chat_with_tutor(message: Message):
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
    with open(prompt_file, "r") as f:
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
    with open(f"./prompts/{language}_tutor.txt", "r") as f:
        system_prompt = f.read()
    
    if level == "novice":
        exercise_types = ["TRANSLATION"]
    elif level == "beginner":
        exercise_types = ["TRANSLATION","MULTIPLE_CHOICE","CONJUGATION"]
        exercise_types = ["MULTIPLE_CHOICE"]
    elif level == "intermediate":
        exercise_types = ["CONJUGATION", "TRANSLATION"]
    else:
        exercise_types = ["TRANSLATION"]
        
    exercise_type = random.choice(exercise_types)
    print(exercise_type)
    print(level)
    cefr = get_cefr(level)

    correct_mc = "" # to store correct word for multiple choice

    # generate prompt for exercises
    if exercise_type == "TRANSLATION":
        prompt = (
            f"{system_prompt}\n\n"
            f"Give a word in English that a {level}-level {language} speaker may know in {language}. The word must be of {cefr} cefr level. \n"
            "Provide the response in this format:\n"
            "INSTRUCTIONS: [tell the user to translate the word]\n"
            "CONTENT: [the given word in English]\n"
            f"TARGET: [csv list of {language} translations of the word]\n"
        )
    elif exercise_type == "MULTIPLE_CHOICE":
        
        # GET THE WORD AND ITS TRANSLATION
        while True:
            try:
                prompt = (
                f"{system_prompt}\n\n"
                    f"Give a word in English that a {level}-level {language} speaker may know in {language}. The word must be of {cefr} cefr level. \n"
                    "Provide the response in this format:\n"
                    "INSTRUCTIONS: [tell the user to translate the word]\n"
                    "CONTENT: [the given word in English]\n"
                    f"TARGET: [csv list of {language} translations of the word]\n"
                )
                # print(prompt)
                response = requests.post(
                    OLLAMA_URL,
                    json={
                        "model": "llama3",
                        "prompt": prompt,
                        "stream": False,
                        "system": system_prompt
                    },
                    timeout=30
                )
                response.raise_for_status()
                
                content = response.json()["response"]
                # print(content)
                parts = {
                    "instructions": "",
                    "content": "",
                    "target": []
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
            current_section = None
            flag = False
            for line in content.split('\n'):
                if line.startswith("INSTRUCTIONS:"):
                    current_section = "instructions"
                    parts["instructions"] = line.split("INSTRUCTIONS:")[1].strip()
                elif line.startswith("CONTENT:"):
                    current_section = "content"
                    parts["content"] = line.split("CONTENT:")[1].strip()
                    if parts["content"] in practiced_words: # run it back if the word has already been practiced
                        print("Restarting prompt...")
                        flag = True
                        break
                    practiced_words.append(parts["content"])
                    #print(parts["content"])
                    #print(practiced_words)
                elif line.startswith("TARGET:"):
                    current_section = "target"
                    parts["target"] = [x.strip() for x in line.split("TARGET:")[1].split(',')]
                    print("Target is: " + str(parts["target"]))
                elif current_section and line.strip():
                    parts[current_section] += "\n" + line.strip()
            if not flag:
                practiced_words.append(parts["content"])
                break
        
        translated_word = parts["target"][0]
        english_word = parts["content"]
        print("\n")
        print(translated_word)
        print(english_word)
        print("\n")
        correct_mc = english_word
        prompt = (
            f"{system_prompt}\n\n"
            f"Generate a {exercise_type} vocabulary exercise for {level} level with:\n"
            "- Clear instructions in English\n"
            f"- {language} word is {translated_word}\n"
            f"- correct answer is {translated_word}. Choose a letter to correspond to it (A-C)\n"
            "- Very simple format\n" 
        )
    elif exercise_type == "CONJUGATION":
        prompt = (
            f"{system_prompt}\n\n"
            f"Generate a {exercise_type} vocabulary exercise for {level} level with:\n"
            "- Clear instructions in English\n"
            "- 1 target vocabulary word\n"
            "- Very simple format\n"
        )
    
    while True:
        try:
            response = requests.post(
                OLLAMA_URL,
                json={
                    "model": "llama3",
                    "prompt": prompt,
                    "stream": False,
                    "system": system_prompt
                },
                timeout=30
            )
            response.raise_for_status()
            
            content = response.json()["response"]
            parts = {
                "instructions": "",
                "content": "",
                "target": []
            }
            
            current_section = None
            flag = False
            for line in content.split('\n'):
                if line.startswith("INSTRUCTIONS:"):
                    current_section = "instructions"
                    parts["instructions"] = line.split("INSTRUCTIONS:")[1].strip()
                elif line.startswith("CONTENT:"):
                    current_section = "content"
                    parts["content"] = line.split("CONTENT:")[1].strip()
                    if exercise_type == "TRANSLATION" and parts["content"] in practiced_words: # run it back if the word has already been practiced
                        print("Restarting prompt...")
                        flag = True
                        break
                    practiced_words.append(parts["content"])
                elif line.startswith("TARGET:"):
                    current_section = "target"
                    parts["target"] = [x.strip() for x in line.split("TARGET:")[1].split(',')]
                    print("Target is: " + str(parts["target"]))

                    if exercise_type == "MULTIPLE_CHOICE":
                        print("Got here")
                        print("target is " + str(parts["target"]))
                        print("target[0] is " + str(parts["target"][0]))
                        if len(parts["target"][0])>1: # FIX: sometimes the format of the multiple choice questions comes out a little strange, so this fixes it
                            flag = True
                            if ") " in parts["target"]:
                                print("flag0 or 1")
                                flag = True
                            break
                        if type(parts["target"]) is str:
                            if ")" in parts["target"]:
                                print("Flag 1")
                                flag = True
                                break
                        if ")" in parts["target"]:
                            print("Here")
                            flag = True
                            break
                        if ")" in parts["target"][0]:
                            print("Here")
                            flag = True
                            break
                    
                    if(exercise_type == "CONJUGATION"): # FIX: dont wanna practice the same conjugation for the same word
                        for targ in parts["target"]:
                            if targ in practiced_translated:
                                flag = True
                                break
                            else:
                                practiced_translated.append(targ)
                elif current_section and line.strip():
                    parts[current_section] += "\n" + line.strip()

            if flag:
                print("redoing")
                continue
            elif (exercise_type == "MULTIPLE_CHOICE") and check_mc(parts, correct_mc):
                print("redoing this one")
                continue
            #print("Practiced words after checking for flag: " + str(practiced_words))
            #print("Practiced translated words after checking for flag: " + str(practiced_translated))
            return {
                "type": exercise_type,
                "raw": content,
                **parts
            }
        except Exception as e:
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