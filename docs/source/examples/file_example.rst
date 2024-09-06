============
File Example
============

.. code-block:: python

    from time import sleep
    
    from collegamento import (
        USER_FUNCTION,
        FileClient,
        FileServer,
        Request,
        Response,
    )
    
    
    def split_str(server: "FileServer", arg: Request) -> list[str]:
        file = arg["file"]  # type: ignore
        return file.split(" ")
    
    
    def main():
        context = FileClient({"test": split_str})
    
        context.update_file("test", "test contents")
        sleep(1)
        context.request({"command": "test", "file": "test"})
    
        sleep(1)
    
        output: Response = context.get_response("test")  # type: ignore
        print(output)
    
        context.kill_IPC()
    
    
    if __name__ == "__main__":
        main()

See the file example file `here <https://github.com/salve-org/albero/blob/master/examples/file_example.py>`_.