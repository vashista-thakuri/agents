from agent import agent

def run_agent_loop(agent):
    print("What do you want to know? Ask me anything or type 'exit' to quit.")
    while True:
        try:
            question = input("\nMe: ")
            if question.lower() in {"exit", "quit"}:
                print("\nGoodbye, talk to you later!")
                break
            response = agent.run(question)
            print(f"Agent: {response}")
        except Exception as e:
            print(f"[Error] {e}")

if __name__ == "__main__":
    from agent import agent
    run_agent_loop(agent)