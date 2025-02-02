import re

def read_lines_from_file(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file.readlines()]

def extract_identifier(text):
    match = re.match(r"(\d+\.\w+)\.", text)
    return match.group(1) if match else None

questions = read_lines_from_file('C:/Users/Lenovo/Desktop/E assessment/backend/question.txt')
answers = read_lines_from_file('C:/Users/Lenovo/Desktop/E assessment/backend/answers.txt')

question_dict = {extract_identifier(q): q for q in questions if extract_identifier(q)}
answer_dict = {extract_identifier(a): a for a in answers if extract_identifier(a)}

matched_pairs = []
for q_id, question in question_dict.items():
    answer = answer_dict.get(q_id)
    if answer:
        matched_pairs.append((question, answer))

# Save matched pairs to a file
output_path = 'C:/Users/Lenovo/Desktop/E assessment/question_answer.txt'
with open(output_path, 'w') as file:
    for question, answer in matched_pairs:
        file.write(f"Question: {question}\n")
        file.write(f"Answer: {answer}\n\n")

print(f"Matched questions and answers saved to {output_path}")
