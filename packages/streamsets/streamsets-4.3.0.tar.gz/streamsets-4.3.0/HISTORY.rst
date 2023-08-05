History
=======


4.3.0 (August 2022)
-------------------
* Added support for using the SDK on Python 3.10

* :py:class:`streamsets.sdk.sch_models.Users` and :py:class:`streamsets.sdk.sch_models.Groups` instances can now be
  filtered on specific text values via the ``filter_text`` parameter, as seen in the UI

* Bug fixes and improvements


4.2.1 (July 2022)
-----------------
* Fixes a bug when trying to modify or update a :py:class:`streamsets.sdk.sch_models.ACL` definition for :py:class:`streamsets.sdk.sch_models.Deployment`
  instances.

* Fixes a bug in the naming convention used for pipelines created via the :py:meth:`streamsets.sdk.ControlHub.test_pipeline_run`
  method.

* Fixes a bug that prevented users from supplying a ``'.'`` (period) character in the ``group_id`` when creating a group
  via the :py:meth:`streamsets.sdk.sch_models.GroupBuilder.build` method.


4.2.0 (May 2022)
----------------
* Programmatic User creation and management has been added

* Pagination and "lazy" loading improvements have been made to various classes

* The Group class has been refactored slightly to better match the experience seen in the UI

.. note::
  When filtering the :py:class:`streamsets.sdk.sch_models.Groups` objects in DataOps Platform, the ``id`` argument has
  been replaced by ``group_id`` to match the :py:class:`streamsets.sdk.sch_models.Group` class's representation. Please
  refer to the documentation for the correct, updated usage.

* The :py:meth:`streamsets.sdk.sch_models.DeploymentBuilder.build` and :py:meth:`streamsets.sdk.sch_models.EnvironmentBuilder.build`
  methods no longer require the ``deployment_type`` or ``environment_type`` arguments to be supplied

.. warning::
  The ``deployment_type`` and ``environment_type`` arguments are deprecated and will be removed in a future release.
  Please refer to the documentation for the correct, updated usage.

* The :py:class:`streamsets.sdk.sch_models.Deployments` and :py:class:`streamsets.sdk.sch_models.Environments` classes
  can now be filtered on ``deployment_id`` and ``environment_id`` respectively, instead of ``id``

.. warning::
  The ``id`` argument has been deprecated and will be removed in a future release. Please refer to the documentation for
  the correct, updated usage.


4.1.0 (March 2022)
--------------------
* Modified error handling to return all errors returned by an API call to DataOps Platform

* Transformer for Snowflake support

* Support for nightly builds of execution engines


4.0.0 (January 2022)
--------------------
* Activation key is no longer required

* DataCollector and Transformer classes are no longer public because these are headless engines in StreamSets DataOps Platform

* Authentication is now handled using API Credentials

* The usage and syntax for PipelineBuilder has been updated

* Support for environments and deployments

