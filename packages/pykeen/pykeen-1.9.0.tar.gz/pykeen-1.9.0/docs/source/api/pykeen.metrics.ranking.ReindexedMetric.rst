ReindexedMetric
===============

.. currentmodule:: pykeen.metrics.ranking

.. autoclass:: ReindexedMetric
   :show-inheritance:

   .. rubric:: Attributes Summary

   .. autosummary::

      ~ReindexedMetric.base_cls
      ~ReindexedMetric.binarize
      ~ReindexedMetric.closed_expectation
      ~ReindexedMetric.closed_variance
      ~ReindexedMetric.increasing
      ~ReindexedMetric.key
      ~ReindexedMetric.needs_candidates
      ~ReindexedMetric.supported_rank_types
      ~ReindexedMetric.supports_weights
      ~ReindexedMetric.synonyms

   .. rubric:: Methods Summary

   .. autosummary::

      ~ReindexedMetric.__call__
      ~ReindexedMetric.adjust
      ~ReindexedMetric.expected_value
      ~ReindexedMetric.get_coefficients
      ~ReindexedMetric.get_description
      ~ReindexedMetric.get_link
      ~ReindexedMetric.get_range
      ~ReindexedMetric.get_sampled_values
      ~ReindexedMetric.numeric_expected_value
      ~ReindexedMetric.numeric_expected_value_with_ci
      ~ReindexedMetric.numeric_variance
      ~ReindexedMetric.numeric_variance_with_ci
      ~ReindexedMetric.std
      ~ReindexedMetric.variance

   .. rubric:: Attributes Documentation

   .. autoattribute:: base_cls
   .. autoattribute:: binarize
   .. autoattribute:: closed_expectation
   .. autoattribute:: closed_variance
   .. autoattribute:: increasing
   .. autoattribute:: key
   .. autoattribute:: needs_candidates
   .. autoattribute:: supported_rank_types
   .. autoattribute:: supports_weights
   .. autoattribute:: synonyms

   .. rubric:: Methods Documentation

   .. automethod:: __call__
   .. automethod:: adjust
   .. automethod:: expected_value
   .. automethod:: get_coefficients
   .. automethod:: get_description
   .. automethod:: get_link
   .. automethod:: get_range
   .. automethod:: get_sampled_values
   .. automethod:: numeric_expected_value
   .. automethod:: numeric_expected_value_with_ci
   .. automethod:: numeric_variance
   .. automethod:: numeric_variance_with_ci
   .. automethod:: std
   .. automethod:: variance
