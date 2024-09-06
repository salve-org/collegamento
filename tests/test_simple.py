from time import sleep

from collegamento import Response, Client


def foo(server, request):
    print("Foo called", request["id"])


def main():
    Client({"foo": foo})
    x = Client({"foo": (foo, True), "foo2": foo})

    x.request({"command": "foo"})
    x.request({"command": "foo"})
    x.request({"command": "foo2"})
    x.request(
        {"command": "foo2"}
    )  # If you see six "Foo called"'s, thats bad news bears
    x.add_command("foo3", foo)
    x.request({"command": "foo3"})
    x.add_command("foo4", foo, True)
    x.request({"command": "foo4"})
    x.request({"command": "foo4"})

    sleep(1)

    x.check_responses() # Not necessary, we're just checking that doing
    # this first doesn't break get_response

    foo_r: list[Response] = x.get_response("foo")
    foo_two_r: list[Response] = x.get_response("foo2")
    foo_three_r: list[Response] = x.get_response("foo3")
    foo_four_r: list[Response] = x.get_response("foo4")

    assert len(foo_r) == 2
    assert len(foo_two_r) == 1
    assert len(foo_three_r) == 1
    assert len(foo_four_r) == 2

    x.check_responses()
    x.create_server()

    Client()
    Client({"foo": foo}).request({"command": "foo"})
    Client().kill_IPC()
    Client().create_server()

    sleep(1)


if __name__ == "__main__":
    main()
