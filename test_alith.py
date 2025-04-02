from alith import Agent

def main():
    # Create an Agent using GPT-4 with a comedic role
    agent = Agent(
        name="Comedian Agent",
        model="gpt-4",
        preamble="You are a stand-up comedian who cracks jokes and makes people laugh."
    )

    # Prompt the agent
    user_message = "Entertain me with a short joke!"
    response = agent.prompt(user_message)

    print("AI Agent Response:", response)

if __name__ == "__main__":
    main()
