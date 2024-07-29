=============
Class Example
=============

.. code-block:: python

    from time import sleep
    
    from collegamento import FileClient, Request
    
    
    class MyClient:
        def __init__(self):
            self.context = FileClient({"MyClientFunc": self.split_str})
    
            self.context.update_file("user_file", "")
    
        def change_file(self, new_contents: str) -> None:
            self.context.update_file("user_file", new_contents)
    
        def request_split(self) -> None:
            self.context.request({"command": "MyClientFunc", "file": "user_file"})
    
        def check_split(self) -> list[str] | None:
            output = self.context.get_response("MyClientFunc")
            if output is not None:
                return output["result"]  # type: ignore
            return output
    
        def split_str(self, arg: Request) -> list[str]:
            file = arg["file"]  # type: ignore
            return file.split(" ")
    
    
    def main():
        mc = MyClient()
        mc.change_file("Test File")
        mc.request_split()
    
        sleep(1)
    
        output = mc.check_split()
        print(output)
    
    
    if __name__ == "__main__":
        main()

See the file example file `here <https://github.com/salve-org/albero/blob/master/examples/class_example.py>`_.