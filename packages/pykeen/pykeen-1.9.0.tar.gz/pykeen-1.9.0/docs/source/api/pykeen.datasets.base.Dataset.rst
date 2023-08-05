Dataset
=======

.. currentmodule:: pykeen.datasets.base

.. autoclass:: Dataset
   :show-inheritance:

   .. rubric:: Attributes Summary

   .. autosummary::

      ~Dataset.create_inverse_triples
      ~Dataset.entity_to_id
      ~Dataset.factory_dict
      ~Dataset.metadata
      ~Dataset.metadata_file_name
      ~Dataset.num_entities
      ~Dataset.num_relations
      ~Dataset.relation_to_id

   .. rubric:: Methods Summary

   .. autosummary::

      ~Dataset.cli
      ~Dataset.deteriorate
      ~Dataset.docdata
      ~Dataset.from_directory_binary
      ~Dataset.from_path
      ~Dataset.from_tf
      ~Dataset.get_normalized_name
      ~Dataset.remix
      ~Dataset.similarity
      ~Dataset.summarize
      ~Dataset.summary_str
      ~Dataset.to_directory_binary
      ~Dataset.triples_pair_sort_key
      ~Dataset.triples_sort_key

   .. rubric:: Attributes Documentation

   .. autoattribute:: create_inverse_triples
   .. autoattribute:: entity_to_id
   .. autoattribute:: factory_dict
   .. autoattribute:: metadata
   .. autoattribute:: metadata_file_name
   .. autoattribute:: num_entities
   .. autoattribute:: num_relations
   .. autoattribute:: relation_to_id

   .. rubric:: Methods Documentation

   .. automethod:: cli
   .. automethod:: deteriorate
   .. automethod:: docdata
   .. automethod:: from_directory_binary
   .. automethod:: from_path
   .. automethod:: from_tf
   .. automethod:: get_normalized_name
   .. automethod:: remix
   .. automethod:: similarity
   .. automethod:: summarize
   .. automethod:: summary_str
   .. automethod:: to_directory_binary
   .. automethod:: triples_pair_sort_key
   .. automethod:: triples_sort_key
