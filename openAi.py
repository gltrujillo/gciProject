import openai

# Set up your API key
openai.api_key = "YOUR_API_KEY"

def generate_response(prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150
    )
    return response.choices[0].text.strip()

def chat_with_ai():
    print("Start chatting with the AI (type 'exit' to quit):")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break
        response = generate_response(user_input)
        print(f"AI: {response}")

if __name__ == "__main__":
    chat_with_ai()
#The generate_response function sends the user's prompt to OpenAI's API and returns the generated response.
#The chat_with_ai function allows a simple conversation with the AI, where users can type input, and the AI responds. You can quit by typing "exit." 
