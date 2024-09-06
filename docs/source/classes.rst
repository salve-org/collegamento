=======
Classes
=======

.. _CollegamentoError Overview:

``CollegamentoError``
*********************

The ``CollegamentoError`` class is a simple error class for ``Collegamento``.

.. _Request Overview:

``Request``
***********

The ``Request`` class is a TypedDict meant to provide a framework for items given to functions used by the IPC. It *will* almsot always contain extra items regardless of the fact that that's not supposed to happen (just add ``# type: ignore`` to the end of the line to shut up the langserver). The data provided will not be typed checked to make sure its proper. The responsibility of data rests on the user.

.. _Response Overview:

``Response``
************

The ``Response`` class is what is returned by the "ref:`Client Overview` or one of it's variants to the user. The useful data is found at ``some_response["result"]``.

.. _Client Overview:

``Client``
****************

The ``Client`` class can do:

- ``Client.request(command: str, **kwargs)``
- ``Client.add_command(name: str, command: USER_FUNCTION, multiple_requests: bool = False)`` (adds the function with the name provided that takes input of :ref:`Request Overview` and returns anything)
- ``Client.get_response(command: str) -> Response | list[Response] | None`` (returns a list of ``Response``'s if the command allows multiple requests otherwise a single ``Response`` if there is were any responses ohterwise ``None``)
- ``Client.kill_IPC()`` (kills the IPC server)

When using the ``Client`` class you give the commands as a dict. Below are the ways it can be specified:
 - ``{"foo": foo}`` (this means the command foo can only take the newest request given
 - ``{"foo": (foo, False)}`` (this means the command foo can only take the newest request given
 - ``{"foo": (foo, True)}`` (this means the command foo can take all requests given (new or old)

By default ``Collegamento`` assumes you only want the newest request but chooses to still give the option to make multiple requests. For ``.get_response()`` the output changes based on how this was specified by giving ``None`` if there was no response, ``Response`` if the command only allows the newest request, and ``list[Response]`` if it allows multiple regardless of how many times you made a request for it.

Note that because of the way that the commands are handed to the ``Server`` and run, they can actually modify its attributes and theoretically even the functions the ``Server`` runs. This high flexibility also requires the user to ensure that they properly manage any attributes they mess with.

When it comes to requesting the server to run a command, you give the command as the first argument and all subsequent args for the function the ``Server`` calls are given as kwargs that are passed on.

.. _Server Overview:

``Server``
****************

The ``Server`` is a backend piece of code made visible for commands that can be given to a ``Client``. If you want to know more about it, check out the source code ;). The reason it is mentioned is because it is given as an argument to :ref:`USER_FUNCTION Overview`'s and we choose to let type declarations exist.

.. _FileClient Overview:

``FileClient``
**************

``FileClient`` has the additional methods:

- ``FileClient.update_file(file: str, current_state: str)`` (adds or updates the file with the new contents and notifies server of changes)
- ``FileClient.remove_file(file: str)`` (removes the file specified from the system and notifies the server to fo the same)

This class also has some changed functionality. When you make a ``.request()`` and add a file to the request, it changes the request's file name to its contents for the function to use. This isn't technically necessary as the function called can access the files in the Server and modify them as it pleases since it has full access to all the Server's resources.

.. _FileServer Overview:

``FileServer``
**************

The ``FileServer`` is a backend piece of code made visible for commands that can be given to a ``FileClient``. See my explanation on :ref:`Server Overview`
