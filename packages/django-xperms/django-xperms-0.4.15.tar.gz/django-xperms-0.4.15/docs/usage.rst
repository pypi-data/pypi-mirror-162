=====
Usage
=====

To use django-xperms in a project, add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'xperms.apps.XPermsConfig',
        ...
    )

Add django-xperms's URL patterns:

.. code-block:: python

    from xperms import urls as xperms_urls


    urlpatterns = [
        ...
        url(r'^', include(xperms_urls)),
        ...
    ]
