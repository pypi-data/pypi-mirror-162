pyqalx
======
.. image:: https://img.shields.io/bitbucket/pipelines/agiletekengineering/pyqalx   :alt: Bitbucket Pipelines


.. image:: https://api.codacy.com/project/badge/Grade/fdfb81fd286a474098b624b426d63c41
    :target: https://www.codacy.com?utm_source=bitbucket.org&amp;utm_medium=referral&amp;utm_content=agiletekengineering/pyqalx&amp;utm_campaign=Badge_Grade


.. image:: https://api.codacy.com/project/badge/Coverage/fdfb81fd286a474098b624b426d63c41
    :target: https://www.codacy.com?utm_source=bitbucket.org&amp;utm_medium=referral&amp;utm_content=agiletekengineering/pyqalx&amp;utm_campaign=Badge_Coverage


Interfaces to qalx. For more details, see `project documentation, <http://docs.qalx.net>`_.

.. admonition:: development status

   ``pyqalx`` is currently under active development. It is pre-version 1.0 beta software and so each minor version
   can introduce breaking changes.

**qalx** (an abbreviation of "queued calculations" and pronounced "kal-x") is a flexible data management platform for engineering projects. Users store data and files in qalx and it provides tools for passing that data between various systems for processing.

There will eventually be four ways to interact with the platform:

-  A Python interface (pyqalx)
-  REST API (api.qalx.net)
-  Web console (console.qalx.net) - coming soon
-  A command line interface (qalx-cli) - coming soon

Most users are expected to use the web console and either the python or
command line interfaces. The REST API is intended to be used if you
prefer to access the platform with a language other than Python or want
to create a custom interface.

.. _installing:

Installing
==========

**qalx** is written in `Python <https://python.org>`_ and can be
installed via the Python Package Index (PyPi) with:

.. code:: bash

   pip install pyqalx

If installation has completed properly you should be able to import
``pyqalx`` in a python console:

>>> import pyqalx

.. warning::

      pyqalx requires **Python versions above 3.6**.


Configuration and Authentication
--------------------------------

Everything you do with **qalx** requires you to be authenticated. That
is, the platform requires you to identify yourself and will record all
your actions as being performed by you.

The way that **qalx** knows who you are is by reading a ``TOKEN``
which must be sent with every request.

.. warning::
   During this beta phase, you have to request a ``TOKEN`` by registering your interest at `qalx.net <https://qalx.net>`_

The easiest way to make sure that your token is sent with every request is to make sure you have a valid ``.qalx`` file
saved in your HOME directory.

.. admonition::  where is ``HOME``?

   The ``HOME`` directory can usually be found by putting %USERPROFILE%
   in the address bar in Windows Explorer or it is simply ``~`` on unix
   systems.


qalx CLI configure
------------------
You can either add the ``TOKEN`` manually to the config file or you can use the **qalx** cli to do this for you automatically

.. code:: bash

   $ qalx configure

The above command will ask you all the necessary questions to create your user and bot config files.

You can also create other profiles using the ``qalx configure`` command. You can even create profiles just for bots
or just for users - or provide extra arguments to write to the config

.. code:: bash

   # Will write a user profile called `dev` to the config file,
   # will also write a `default` bot config profile
   $ qalx --user-profile dev configure

   # Will write a bot profile called `dev` to the config file,
   # will also write a `default` user config profile
   $ qalx --bot-profile dev configure

   # Will not write the bot profile
   $ qalx configure --no-bot

   # Will not write the user profile
   $ qalx configure --no-user

   # Will write a default user and bot profile and will also write two
   # extra keys to each config - `CUSTOMKEY=customvalue`
   # and `CUSTOMKEY2=customvalue2`
   $ qalx configure customkey=customvalue customkey2=customvalue2

Manual configuration
--------------------

If you don't want to use the ``qalx cli`` to configure your profile (or if you want to make changes to it in the future)
then you can configure the profile yourself by adding the ``TOKEN`` to your config file under
the default profile.

.. code:: ini

   [default]
   TOKEN = 632gd7yb9squd0q8sdhq0s8diqsd0nqsdq9sdk

Any other configuration settings can be stored in the same file see `<configuration>`_ for more information.

Quickstart
----------

The best place to get started: `<https://docs.qalx.net/quickstart>`_



