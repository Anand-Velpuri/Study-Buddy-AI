import os
import streamlit as st
import pandas as pd
from src.generator.question_generator import QuestionGenerator
from datetime import datetime


def rerun():
    st.session_state["rerun_trigger"] = not st.session_state.get("rerun_trigger", False)


class QuizManager:
    def __init__(self):
        self.questions = []
        self.results = []
    
    def generate_questions(self, generator: QuestionGenerator, topic: str, question_type: str, difficulty: str, num_questions: int):
        self.questions = []
        self.results = []

        try:
            # ONE batched LLM call that returns the strictly typed suite
            quiz_suite = generator.generate_questions_suite(topic, question_type, difficulty.lower(), num_questions)
            
            # Unpack based on the requested type (since Pydantic guarantees the structure now)
            if question_type == "Multiple Choice":
                for question in quiz_suite.questions:
                    self.questions.append({
                        "type": "MCQ",
                        "question": question.question,
                        "options": question.options,
                        "correct_answer": question.correct_answer
                    })
            elif question_type == "Fill in the Blank":
                for question in quiz_suite.questions:
                    self.questions.append({
                        "type": "Fill in the Blank",
                        "question": question.question,
                        "correct_answer": question.answer
                    })

        except Exception as e:
            st.error(f"Error generating questions: {e}")
            raise Exception(f"Error generating questions: {e}")
        
        return True
    
    def attempt_quiz(self):
        for i, q in enumerate(self.questions):
            # Fixed the double quotes inside the f-string to single quotes
            st.markdown(f"**Question {i + 1} : {q['question']}**")

            if q["type"] == "MCQ":
                # We render the widget and assign a key. 
                # Streamlit automatically saves the user's choice to st.session_state
                st.radio(
                    f"Select an answer for Question {i + 1}",
                    options=q["options"],
                    key=f"mcq_{i}"
                )
            else:
                st.text_input(
                    f"Fill in the blank for Question {i + 1}",
                    key=f"fill_blank_{i}"
                )
    
    def evaluate_quiz(self):
        self.results = []

        for i, q in enumerate(self.questions):
            # Fetch the user's exact answer directly from session_state using the key
            if q["type"] == "MCQ":
                user_ans = st.session_state.get(f"mcq_{i}", "")
            else:
                user_ans = st.session_state.get(f"fill_blank_{i}", "")

            result_dict = {
                "question_number": i+1,
                "question": q["question"],
                "question_type": q["type"],
                "user_answer": user_ans,
                "correct_answer": q["correct_answer"],
                "is_correct": False
            }
            
            if q["type"] == "MCQ":
                result_dict["options"] = q["options"]
                result_dict["is_correct"] = user_ans == q["correct_answer"]
            else:
                result_dict["options"] = []
                result_dict["is_correct"] = user_ans.strip().lower() == q["correct_answer"].strip().lower()
            
            self.results.append(result_dict)
    
    def generate_results_dataframe(self):
        if not self.results:
            return pd.DataFrame()  # Return an empty DataFrame if there are no results
        
        return pd.DataFrame(self.results)
    
    def save_to_csv(self, filename_prefix="quiz_results"):
        if not self.results:
            st.warning("No results to save !!!")
            return
        
        df = self.generate_results_dataframe()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{filename_prefix}_{timestamp}.csv"

        os.makedirs("results", exist_ok=True)

        full_path = os.path.join("results", filename)

        try:
            df.to_csv(full_path, index=False)
            st.success(f"Results saved to {full_path}")
            return full_path
        except Exception as e:
            st.error(f"Failed to save results: {e}")
            return None