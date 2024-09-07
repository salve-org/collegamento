=============
Example Usage
=============

Now that you have ``Collegamento`` installed, let's try running a simple example that should print out ``"Yippee! It worked!"``:

.. code-block:: python

    from time import sleep

    from collegamento import Client, Request, Response, Server


    def foo(server: "Server", bar: Request) -> bool:
        if bar["command"] == "test":
            return True
        return False


    def main():
        # As of collegamento v0.3.0 you can allow multiple requests for the same command
        # like so: {"test": (foo, True)} (using (foo, False)) is the default (only newest request)
        context = Client({"test": foo})

        context.request("test")

        sleep(1)

        output: Response = context.get_response("test")  # type: ignore
        if output and output[0]["result"]:  # type: ignore
            print("Yippee! It worked!")
        else:
            print("Aww, maybe your computer is just a little slow?")

        context.kill_IPC()


    if __name__ == "__main__":
        main()
