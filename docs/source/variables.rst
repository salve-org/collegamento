=========
Variables
=========

.. _USER_FUNCTION Overview:

``USER_FUNCTION``
*****************

``USER_FUNCTION`` is a type variable that simply states that any function that matches this type takes in a :ref:`Server Overview` and :ref:`Request Overview` class (positionally) and can return anything it pleases (though this will never be used).

.. _COMMANDS_MAPPING Overview:

``COMMANDS_MAPPING``
********************

``COMMANDS_MAPPING`` is a type variable that states that any dictionary that matches this type has keys that are strings and values that are either functions that match the :ref:`USER_FUNCTION Overview` type or a tuple with that function and a boolean that indicates whether the function can have multiple :ref:``Request Overview``'s.
