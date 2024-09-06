from time import sleep

from collegamento import Client, Response


def foo(server, request):
    print("Foo called", request["id"])


def test_normal_client():
    Client({"foo": foo})
    x = Client({"foo": (foo, True), "foo2": foo})

    x.request("foo")
    x.request("foo")
    x.request("foo2")
    x.request("foo2")  # If you see six "Foo called"'s, thats bad news bears
    x.add_command("foo3", foo)
    x.request("foo3")
    x.add_command("foo4", foo, True)
    x.request("foo4")
    x.request("foo4")

    sleep(1)

    x.check_responses()  # Not necessary, we're just checking that doing
    # this first doesn't break get_response

    foo_r: list[Response] = x.get_response("foo")  # type: ignore
    foo_two_r: Response = x.get_response("foo2")  # type: ignore
    foo_three_r: Response = x.get_response("foo3")  # type: ignore
    foo_four_r: list[Response] = x.get_response("foo4")  # type: ignore

    assert len(foo_r) == 2
    assert foo_two_r
    assert foo_three_r
    assert len(foo_four_r) == 2

    x.check_responses()
    x.create_server()

    assert x.all_ids == []

    Client()
    Client({"foo": foo}).request("foo")
    Client().kill_IPC()
    Client().create_server()

    sleep(1)
