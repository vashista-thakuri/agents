from agent import agent

if __name__ == "__main__":
    print("What do you want to know? Ask me anything or Type 'exit/quit' to quit.")
    while True:
        question = input("\nMe: ")
        if question.lower() in {"exit", "quit"}:
            print("\nGoodbye, talk to you later!")
            break
        response = agent.run(question)
        print(f"Agent: {response}")