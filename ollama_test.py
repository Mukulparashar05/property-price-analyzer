from ollama import Client


def main() -> None:
    client = Client(host="http://127.0.0.1:11434")
    response = client.generate(
        model="qwen2.5:7b",
        prompt="Say happy in one short sentence.",
    )
    print(response.response)


if __name__ == "__main__":
    main()
