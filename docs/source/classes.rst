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

The ``Response`` class is what is returned by the "ref:`SimpleClient Overview` or one of it's variants to the user. The useful data is found at ``some_response["result"]``.

.. _SimpleClient Overview:

``SimpleClient``
****************

The ``SimpleClient`` class can do:

- ``SimpleClient.request(request_details: dict)`` (all details in request_details are specific to the command in the request_details)
- ``SimpleClient.add_command(name: str, command: USER_FUNCTION)`` (adds the function with the name provided that takes input of :ref:`Request Overview` and returns anything``
- ``SimpleClient.kill_IPC()`` (kills the IPC server)

.. _SimpleServer Overview:

``SimpleServer``
****************

The SimpleServer is a backend piece of code made visible for commands that can be given to a ``SimpleClient``. If you want to know more about it, check out the source code ;).

.. _FileClient Overview:

``FileClient``
**************

``FileClient`` has the additional methods:

- ``FileClient.update_file(file: str, current_state: str)`` (adds or updates the file with the new contents and notifies server of changes)
- ``FileClient.remove_file(file: str)`` (removes the file specified from the system and notifies the server to fo the same)

This class also has some changed functionality. When you make a ``.request()`` and add a file to the request, it chnages the request's name to its contents for the function to use.

.. _FileServer Overview:

``FileServer``
**************

The ``FileServer`` is a backend piece of code made visible for commands that can be given to a ``FileClient``. If you want to know more about it, check out the source code ;).
