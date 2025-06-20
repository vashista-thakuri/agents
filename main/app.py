from agent import agent

if __name__ == "__main__":
    while True:
        question = input("User: ")
        if question.lower() in {"exit", "quit"}:
            break
        response = agent.run(question)
        print(f"Agent: {response}")