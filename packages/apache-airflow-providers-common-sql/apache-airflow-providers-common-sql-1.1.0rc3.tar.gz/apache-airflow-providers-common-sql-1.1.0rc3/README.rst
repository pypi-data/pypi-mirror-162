
.. Licensed to the Apache Software Foundation (ASF) under one
   or more contributor license agreements.  See the NOTICE file
   distributed with this work for additional information
   regarding copyright ownership.  The ASF licenses this file
   to you under the Apache License, Version 2.0 (the
   "License"); you may not use this file except in compliance
   with the License.  You may obtain a copy of the License at

..   http://www.apache.org/licenses/LICENSE-2.0

.. Unless required by applicable law or agreed to in writing,
   software distributed under the License is distributed on an
   "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
   KIND, either express or implied.  See the License for the
   specific language governing permissions and limitations
   under the License.


Package ``apache-airflow-providers-common-sql``

Release: ``1.1.0rc3``


`Common SQL Provider <https://en.wikipedia.org/wiki/SQL>`__


Provider package
----------------

This is a provider package for ``common.sql`` provider. All classes for this provider package
are in ``airflow.providers.common.sql`` python package.

You can find package information and changelog for the provider
in the `documentation <https://airflow.apache.org/docs/apache-airflow-providers-common-sql/1.1.0/>`_.


Installation
------------

You can install this package on top of an existing Airflow 2 installation (see ``Requirements`` below
for the minimum Airflow version supported) via
``pip install apache-airflow-providers-common-sql``

The package supports the following python versions: 3.7,3.8,3.9,3.10

Requirements
------------

=============  ==================
PIP package    Version required
=============  ==================
``sqlparse``   ``>=0.4.2``
=============  ==================

 .. Licensed to the Apache Software Foundation (ASF) under one
    or more contributor license agreements.  See the NOTICE file
    distributed with this work for additional information
    regarding copyright ownership.  The ASF licenses this file
    to you under the Apache License, Version 2.0 (the
    "License"); you may not use this file except in compliance
    with the License.  You may obtain a copy of the License at

 ..   http://www.apache.org/licenses/LICENSE-2.0

 .. Unless required by applicable law or agreed to in writing,
    software distributed under the License is distributed on an
    "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
    KIND, either express or implied.  See the License for the
    specific language governing permissions and limitations
    under the License.

.. NOTE TO CONTRIBUTORS:
    Please, only add notes to the Changelog just below the "Changelog" header when there are some breaking changes
    and you want to add an explanation to the users on how they are supposed to deal with them.
    The changelog is updated and maintained semi-automatically by release manager.


Changelog
---------

1.1.0
.....

Features
~~~~~~~~

* ``Improve taskflow type hints with ParamSpec (#25173)``
* ``Move all "old" SQL operators to common.sql providers (#25350)``
* ``Deprecate hql parameters and synchronize DBApiHook method APIs (#25299)``
* ``Unify DbApiHook.run() method with the methods which override it (#23971)``
* ``Common SQLCheckOperators Various Functionality Update (#25164)``

Bug Fixes
~~~~~~~~~

* ``Allow Legacy SqlSensor to use the common.sql providers (#25293)``
* ``Fix fetch_all_handler & db-api tests for it (#25430)``
* ``Align Common SQL provider logo location (#25538)``

1.0.0
.....

Initial version of the provider.
Adds ``SQLColumnCheckOperator`` and ``SQLTableCheckOperator``.
Moves ``DBApiHook``, ``SQLSensor`` and ``ConnectorProtocol`` to the provider.
