from time import sleep

from collegamento import (
    USER_FUNCTION,
    Request,
    Response,
    Client,
    Server,
)


def foo(server: "Server", bar: Request) -> bool:
    if bar["command"] == "test":
        return True
    return False


def main():
    context = Client({"test": foo})

    context.request({"command": "test"})

    sleep(1)

    output: list[Response] = context.get_response("test")
    if output and output[0]["result"]:  # type: ignore
        print("Yippee! It worked!")
    else:
        print("Aww, maybe your computer is just a little slow?")

    context.kill_IPC()


if __name__ == "__main__":
    main()
