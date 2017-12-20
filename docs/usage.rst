=====
Usage
=====

To use wrapper_tag in a project, add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'wrapper_tag.apps.WrapperTagConfig',
        ...
    )

Add wrapper_tag's URL patterns:

.. code-block:: python

    from wrapper_tag import urls as wrapper_tag_urls


    urlpatterns = [
        ...
        url(r'^', include(wrapper_tag_urls)),
        ...
    ]
