16.0.0.1.0 (2023-10-10)
~~~~~~~~~~~~~~~~~~~~~~~

**Bugfixes**

- Prevent MRO conflicts when the module is installed at same time as the
  shopinvader_search_engine module. By inheriting from the same *se.indexable.record*
  model, the MRO conflict is avoided. Before this commit we ended up with a
  redefinition of the *product.category* model to inherit from a subclass of
  *se.indexable.record* in the *sale_channel_search_engine_category* module and
  a redefinition of the *product.product* model to inherit from the *se.indexable.record*
  model in the *shopinvader_search_engine* module. This situation was causing
  a MRO conflict. (`#12 <https://github.com/OCA/sale-channel/issues/12>`_)
