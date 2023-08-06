=======
History
=======

1.3.1 (2022-08-07)
------------------

* Add option with cached_ms<0 to force use the cache, or return None

1.3.0 (2022-08-07)
------------------

* Update Toroid API, using new EcoRT2 version 3.00.02

1.2.1 (2021-05-15)
------------------

* Add "get_all_cached" function to call all resquests to get a cached value.

1.2.0 (2021-05-14)
------------------

* Add "cached" possibilities to reduce the number of call to the API.
* The cached possibilities can be defined directly to the ecodevices_rt2 object (applicable to each call), or to a specific call on a property.

1.1.0 (2021-04-17)
------------------

* Add classes such as `Counter`, `DigitalInput`, `EnOcean Switch or Sensor`, `Post and Sub-Post`, `Relay`, `SupplierIndex`, `Toroid`, `VirtualOutput`, `X4FP (Heaters)`, `XTHL` for ease of use
* Add tests to cover majority of code
* Add full examples in documentation

1.0.1 (2021-04-12)
------------------

* Update package with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

1.0.0 (2021-04-08)
------------------

* First release on PyPI.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
