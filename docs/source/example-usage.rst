=============
Example Usage
=============

Now that you have ``Collegamento`` installed, let's try running a simple example that should print out ``"Yippee! It worked!"``:

.. code-block:: python

    from time import sleep

    from collegamento import USER_FUNCTION, Request, Response, SimpleClient, SimpleServer


    def foo(server: "SimpleServer", bar: Request) -> bool:
        if bar["command"] == "test":
            return True
        return False


    def main():
        commands: dict[str, USER_FUNCTION] = {"test": foo}
        context = SimpleClient(commands)

        context.request({"command": "test"})

        sleep(1)

        output: Response | None = context.get_response("test")
        if output is not None and output["result"]:  # type: ignore
            print("Yippee! It worked!")
        else:
            print("Aww, maybe your compute is just a little slow?")

        context.kill_IPC()


    if __name__ == "__main__":
        main()
