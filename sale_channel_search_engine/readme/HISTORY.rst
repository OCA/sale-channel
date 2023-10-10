16.0.0.1.0 (2023-10-10)
~~~~~~~~~~~~~~~~~~~~~~~

**Bugfixes**

- Prevent MRO conflicts by avoiding to define a new abstract model based
  on the *se.indexable.record* model. This will prevent the MRO conflict when
  one addon extends an existing model to make it indexable by inheriting from the
  *se.indexable.record* model and another addon extends the same model and makes
  it indexable by inheriting from a subclass of *se.indexable.record*. (`#12 <https://github.com/OCA/sale-channel/issues/12>`_)
