import requests
import re
import time

# Define the API URL
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"

# Replace with your Hugging Face API token
HEADERS = {"Authorization": f"Bearer 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"}

# Function to read question-answer pairs from file
def read_question_answer_pairs(filename):
    with open(filename, 'r') as file:
        content = file.read().strip().split('\n\n')
    
    pairs = []
    for block in content:
        lines = block.split('\n')
        if len(lines) >= 2:
            question = lines[0].replace("Question: ", "").strip()
            answer = lines[1].replace("Answer: ", "").strip()
            pairs.append((question, answer))
    return pairs

# Extract marks from the question
def extract_marks(question):
    match = re.search(r"\((\d+)\s*M\)", question)
    return int(match.group(1)) if match else 10  # Default to 10 marks

# Function to get correct answer using API
def get_correct_answer(clean_question, min_words, max_words):
    prompt = f"""Generate a scientifically accurate answer for the following question.
    Ensure the answer contains approximately {min_words} to {max_words} words.

    Question: {clean_question}"""
    
    response = requests.post(API_URL, headers=HEADERS, json={"inputs": prompt})
    return response.json()[0]['generated_text']

# Function to grade student's answer
def grade_answer(question, student_answer, correct_answer, total_marks):
    grading_prompt = f"""Compare the student's answer with the correct answer and assign a score out of {total_marks}.
    Give a score based on factual correctness and logical accuracy. Do NOT explain, just provide the score.

    Question: {question}
    Correct Answer: {correct_answer}
    Student's Answer: {student_answer}

    Provide the score in the format: "Score: X out of {total_marks}"
    """

    response = requests.post(API_URL, headers=HEADERS, json={"inputs": grading_prompt})
    graded_response = response.json()[0]['generated_text']
    
    match = re.search(r"Score:\s*(\d+)\s*out\s*of\s*(\d+)", graded_response)
    return int(match.group(1)) if match else total_marks

# Function to apply word-length penalty
def apply_word_penalty(student_words, model_marks, total_marks, max_words):
    word_penalty_map = {
        2: [(15, 25, 1), (40, 50, 0.5)],
        5: [(100, 120, 2), (150, 170, 1)],
        10: [(400, 450, 3), (500, 520, 2)]
    }
    
    penalties = word_penalty_map.get(total_marks, [])
    reduction = 0

    if student_words > max_words:
        return model_marks

    if student_words < penalties[0][0]:  
        extreme_penalty = {2: 1, 5: 2.5, 10: 5}
        reduction = extreme_penalty.get(total_marks, 0)

    else:
        for i in range(len(penalties)):
            min_w, max_w, penalty = penalties[i]
            if min_w <= student_words <= max_w:
                reduction = penalty
                break
            elif i < len(penalties) - 1:
                next_min_w, next_max_w, next_penalty = penalties[i + 1]
                if student_words > max_w and student_words < next_min_w:
                    reduction = (penalty + next_penalty) / 2  
                    break

    final_marks = max(model_marks - reduction, 0)
    return min(final_marks, model_marks)  

# Main function to process all question-answer pairs
def main():
    input_path = 'C:/Users/Lenovo/Desktop/E assessment/backend/question_answer.txt'
    question_answer_pairs = read_question_answer_pairs(input_path)
    
    word_length_map = {2: (70, 80), 5: (200, 250), 10: (600, 650)}

    for question, student_answer in question_answer_pairs:
        total_marks = extract_marks(question)
        clean_question = re.sub(r"\(\d+\s*M\)", "", question).strip()

        min_words, max_words = word_length_map.get(total_marks, (70, 80))
        correct_answer = get_correct_answer(clean_question, min_words, max_words)

        time.sleep(5)  # Avoid rate limits
        model_marks = grade_answer(clean_question, student_answer, correct_answer, total_marks)

        student_word_count = len(student_answer.split())
        final_marks = apply_word_penalty(student_word_count, model_marks, total_marks, max_words)

        print(f"Question: {question}")
        print(f"Student's Answer: {student_answer}")
        print(f"Score: {final_marks}/{total_marks}\n")

        time.sleep(3)  # Avoid rate limits

if __name__ == "__main__":
    main()
