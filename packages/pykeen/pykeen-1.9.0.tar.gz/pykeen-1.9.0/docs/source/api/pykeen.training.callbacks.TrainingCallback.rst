TrainingCallback
================

.. currentmodule:: pykeen.training.callbacks

.. autoclass:: TrainingCallback
   :show-inheritance:

   .. rubric:: Attributes Summary

   .. autosummary::

      ~TrainingCallback.loss
      ~TrainingCallback.model
      ~TrainingCallback.optimizer
      ~TrainingCallback.result_tracker
      ~TrainingCallback.training_loop

   .. rubric:: Methods Summary

   .. autosummary::

      ~TrainingCallback.on_batch
      ~TrainingCallback.post_batch
      ~TrainingCallback.post_epoch
      ~TrainingCallback.post_train
      ~TrainingCallback.pre_step
      ~TrainingCallback.register_training_loop

   .. rubric:: Attributes Documentation

   .. autoattribute:: loss
   .. autoattribute:: model
   .. autoattribute:: optimizer
   .. autoattribute:: result_tracker
   .. autoattribute:: training_loop

   .. rubric:: Methods Documentation

   .. automethod:: on_batch
   .. automethod:: post_batch
   .. automethod:: post_epoch
   .. automethod:: post_train
   .. automethod:: pre_step
   .. automethod:: register_training_loop
