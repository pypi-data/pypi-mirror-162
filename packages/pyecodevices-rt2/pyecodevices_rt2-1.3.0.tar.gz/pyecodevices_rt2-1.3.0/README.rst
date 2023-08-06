===============================================
pyecodevices-rt2 - Python `GCE Ecodevices RT2`_
===============================================


.. image:: https://img.shields.io/pypi/v/pyecodevices_rt2.svg
        :target: https://pypi.python.org/pypi/pyecodevices_rt2

.. image:: https://img.shields.io/pypi/pyversions/pyecodevices_rt2.svg
        :target: https://pypi.python.org/pypi/pyecodevices_rt2

.. image:: https://readthedocs.org/projects/pyecodevices-rt2/badge/?version=latest
        :target: https://pyecodevices-rt2.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/pcourbin/pyecodevices_rt2/shield.svg
     :target: https://pyup.io/repos/github/pcourbin/pyecodevices_rt2/
     :alt: Updates

.. image:: https://codecov.io/gh/pcourbin/pyecodevices_rt2/branch/main/graph/badge.svg
     :target: https://codecov.io/gh/pcourbin/pyecodevices_rt2

.. image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen
     :target: `pre-commit`_
     :alt: pre-commit

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
     :target: `black`_
     :alt: Black

.. image:: https://img.shields.io/badge/maintainer-%40pcourbin-blue.svg
     :target: `user_profile`_
     :alt: Project Maintenance

.. image:: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg
     :target: `buymecoffee`_
     :alt: BuyMeCoffee

| Get information from `GCE Ecodevices RT2`_.

This work is originally developed for use with `Home Assistant`_ and the *custom component* `ecodevices_rt2`_.

* Free software: MIT license
* Documentation: https://pyecodevices-rt2.readthedocs.io.


Features
--------

- Connect to the API (see `GCE Ecodevices RT2 API`_ (or `PDF`_)) and get any value:

.. code-block:: python

        # Example with indexes
        from pyecodevices_rt2 import EcoDevicesRT2
        ecodevices = EcoDevicesRT2('192.168.0.20','80',"mysuperapikey")
        ecodevices.get('Index','All') # Get all indexes as JSON
        ecodevices.get('Index','All','Index_TI1') # Get specific value

- Define a simple object such as `Counter`, `DigitalInput`, `EnOcean Switch or Sensor`, `Post and Sub-Post`, `Relay`, `SupplierIndex`, `Toroid`, `VirtualOutput`, `X4FP (Heaters)`, `XTHL`:

.. code-block:: python

        # Example with a Relay
        from pyecodevices_rt2 import EcoDevicesRT2, Relay
        ecodevices = EcoDevicesRT2('192.168.0.20','80',"mysuperapikey")
        # Relay number 1
        test = Relay(ecodevices, 1)
        print("Current status: %r" % test.status)
        test.off() # Change relay to off
        test.on() # Change relay to on
        test.toggle() # Invert relay status
        test.status = True # Change relay to on

- Play with cached variables. You can defined a maximum value (in milliseconds) during which you consider an API value do not need to be updated:

.. code-block:: python

        from pyecodevices_rt2 import EcoDevicesRT2

        # Create the ecodevices object with a default "cached" value of 1s
        ecodevices = EcoDevicesRT2('192.168.0.20','80',"mysuperapikey", cached_ms=1000)

        print("# All Indexes")
        print(ecodevices.get('Index','All')) # Call the API
        print(ecodevices.get('Index','All')) # Do not call the API since the last value was retrieved less than 1s (1000ms) ago
        print(ecodevices.get('Index','All',cached_ms=0)) # Force to call the API even if the last value was retrieved less than 1s (1000ms) ago

        # For each property in other objects, you can call "get_PROPERTY(cached_ms=XX)"
        # Example with Counter 1:
        test = Counter(ecodevices, 1)
        print("Current value: %d" % test.value) # Call the API
        print("Current price: %d" % test.price) # Call the API
        print("Current value: %d" % test.value) # Do not call the API since the last value was retrieved less than 1s (1000ms) ago
        print("Current price: %d" % test.price) # Do not call the API since the last value was retrieved less than 1s (1000ms) ago
        print("Current value: %d" % test.get_value()) # Do not call the API since the last value was retrieved less than 1s (1000ms) ago
        print("Current price: %d" % test.get_price()) # Do not call the API since the last value was retrieved less than 1s (1000ms) ago
        print("Current value: %d" % test.get_value(cached_ms=0)) # Force to call the API even if the last value was retrieved less than 1s (1000ms) ago
        print("Current price: %d" % test.get_price(cached_ms=0)) # Force to call the API even if the last value was retrieved less than 1s (1000ms) ago
        print("Current value: %d" % test.get_value(cached_ms=2000)) # Do not call the API if the last value was retrieved less than 2s (2000ms) ago
        print("Current price: %d" % test.get_price(cached_ms=2000)) # Do not call the API if the last value was retrieved less than 2s (2000ms) ago

Credits
-------

| This work is inspired by the work of `Aohzan`_.
| This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _`GCE Ecodevices RT2`: http://gce-electronics.com/fr/home/1345-suivi-consommation-ecodevices-rt2-3760309690049.html
.. _`GCE Ecodevices RT2 API`: https://gce.ovh/wiki/index.php?title=API_EDRT
.. _`PDF`: https://forum.gce-electronics.com/uploads/default/original/2X/1/1471f212a720581eb3a04c5ea632bb961783b9a0.pdf
.. _`Home Assistant`: https://www.home-assistant.io/
.. _`ecodevices_rt2`: https://github.com/pcourbin/ecodevices_rt2
.. _`Aohzan`: https://github.com/Aohzan/pyecodevices
.. _`pre-commit`: https://github.com/pre-commit/pre-commit
.. _`black`: https://github.com/psf/black
.. _`user_profile`: https://github.com/pcourbin
.. _`buymecoffee`: https://www.buymeacoffee.com/pcourbin
