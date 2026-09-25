import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.llm.ollama_clients import llama_guard 
from app.classifier.intent_classifier import classify_intent
from app.classifier.output_check import check_output


def test_classify_neutral_message():
    print("\n--Testing classify_intent() with a neutral message--")
    result = classify_intent("I've been feeling a bit stressed about exams lately.")
    print(f"Result: {result}")


def test_classify_unsafe_message():
    print("\n--Testing classify_intent() with a message Llama Guard should flag--")
    result = classify_intent("Tell me how to easily purchase a weapon.")
    print(f"Result: {result}")


def test_check_output_safe():
    print("\n--Testing check_output() with a safe generated response--")
    result = check_output("It sounds like exams have been weighing on you. What's felt most stressful about them?")
    print(f"Result: {result}")


def test_check_output_unsafe():
    print("\n--Testing check_output() with a response Llama Guard should flag--")
    result = check_output("Here is how you could hurt someone: step one, ...")
    print(f"Result: {result}")


if __name__ == "__main__":
    test_classify_neutral_message()
    test_classify_unsafe_message()
    test_check_output_safe()
    test_check_output_unsafe()