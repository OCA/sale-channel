Add a ``shipping`` block to the payload of ``sale_import_base`` (the other keys
of the order are omitted below). All its keys are optional:

.. code-block:: json

    {
        "name": "XX-0001",
        "shipping": {
            "carrier_code": "express",
            "amount": 20.0,
            "promised_date": "2026-09-25T12:00:00Z"
        }
    }

* ``carrier_code`` selects the delivery method with the same *Import code*, or
  the default carrier of the channel when none matches.
* ``amount`` becomes the delivery line of the order when the carrier has
  *Freight charged by the seller*. Otherwise only the carrier is set.
* When no carrier is found the import does not fail: the code and the amount
  are kept on the order, in the *Other Info* tab.
* ``promised_date`` becomes the delivery date (``commitment_date``) of the order.

A connector can override ``_platform_carrier_codes`` of ``sale.channel.importer``
to list the codes of a shipping done by the channel itself. Those codes never
fall back to the default carrier.
