from langchain_core.prompts import PromptTemplate

mcq_prompt_template = PromptTemplate(
    template=(
        "Generate a {difficulty} multiple-choice question about {topic}.\n\n"
        "Return ONLY a JSON object with these exact fields:\n"
        "- 'question': A clear, specific question\n"
        "- 'options': An array of exactly 4 possible answers\n"
        "- 'correct_answer': One of the options that is the correct answer\n\n"
        "Example format:\n"
        '{{\n'
        '    "question": "What is the capital of France?",\n'
        '    "options": ["London", "Berlin", "Paris", "Madrid"],\n'
        '    "correct_answer": "Paris"\n'
        '}}\n\n'
        "Your response:"
    ),
    input_variables=["topic", "difficulty"]
)

fill_blank_prompt_template = PromptTemplate(
    template=(
        "Generate a {difficulty} fill-in-the-blank question about {topic}.\n\n"
        "Return ONLY a JSON object with these exact fields:\n"
        "- 'question': A sentence with '_____' marking where the blank should be\n"
        "- 'answer': The correct word or phrase that belongs in the blank\n\n"
        "Example format:\n"
        '{{\n'
        '    "question": "The capital of France is _____.",\n'
        '    "answer": "Paris"\n'
        '}}\n\n'
        "Your response:"
    ),
    input_variables=["topic", "difficulty"]
)



mcq_suite_prompt_template = PromptTemplate(
    template=(
        "Generate exactly {num_questions} {difficulty} multiple-choice questions about {topic}.\n\n"
        "Return ONLY a JSON object with a single root key 'questions' containing an array of {num_questions} objects.\n"
        "Each object MUST have:\n"
        "- 'question': A clear, specific question\n"
        "- 'options': An array of exactly 4 possible answers\n"
        "- 'correct_answer': One of the options that is the correct answer\n\n"
        "Example format:\n"
        "{{\n"
        "    \"questions\": [\n"
        "        {{\n"
        "            \"question\": \"What is the capital of France?\",\n"
        "            \"options\": [\"London\", \"Berlin\", \"Paris\", \"Madrid\"],\n"
        "            \"correct_answer\": \"Paris\"\n"
        "        }}\n"
        "    ]\n"
        "}}\n\n"
        "Your response:"
    ),
    input_variables=["topic", "difficulty", "num_questions"]
)

fill_blank_suite_prompt_template = PromptTemplate(
    template=(
        "Generate exactly {num_questions} {difficulty} fill-in-the-blank questions about {topic}.\n\n"
        "Return ONLY a JSON object with a single root key 'questions' containing an array of {num_questions} objects.\n"
        "Each object MUST have:\n"
        "- 'question': A sentence with '________' marking where the blank should be\n"
        "- 'answer': The correct word or phrase that belongs in the blank\n\n"
        "Example format:\n"
        "{{\n"
        "    \"questions\": [\n"
        "        {{\n"
        "            \"question\": \"The capital of France is ________.\",\n"
        "            \"answer\": \"Paris\"\n"
        "        }}\n"
        "    ]\n"
        "}}\n\n"
        "Your response:"
    ),
    input_variables=["topic", "difficulty", "num_questions"]
)