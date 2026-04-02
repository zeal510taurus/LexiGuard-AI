from ai_module import ask_ai
from sentiment import analyse_sentiment
from utils import is_number, check_even_odd

chat_history = []

def smart_assistant(user_input):

    chat_history.append(f"You: {user_input}")

    if is_number(user_input):
        num = float(user_input)
        response = f"{num} is {check_even_odd(num)}"

    else:
        try:
            response = ask_ai(user_input)
        except Exception as e:
            response = f"ERROR: {str(e)}"

        sentiment = analyse_sentiment(user_input)
        response += f"\nSentiment: {sentiment}"
    chat_history.append(f"Assistant: {response}")
    return response

while True:
    user_input = input("You:")

    if user_input.lower() == "exit":
        print("Goodbye!")
        break

    result = smart_assistant(user_input)
    print("Assistant:", result)