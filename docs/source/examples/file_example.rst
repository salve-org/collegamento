============
File Example
============

.. code-block:: python

    from time import sleep
    
    from collegamento import USER_FUNCTION, FileClient, Request, Response
    
    
    def split_str(arg: Request) -> list[str]:
        file = arg["file"]  # type: ignore
        return file.split(" ")
    
    
    def main():
        commands: dict[str, USER_FUNCTION] = {"test": split_str}
        context = FileClient(commands)
    
        context.update_file("test", "test contents")
        context.request({"command": "test", "file": "test"})
    
        sleep(1)
    
        output: Response | None = context.get_response("test")
        print(output)
    
        context.kill_IPC()
    
    
    if __name__ == "__main__":
        main()

See the file example file `here <https://github.com/salve-org/albero/blob/master/examples/file_example.py>`_.