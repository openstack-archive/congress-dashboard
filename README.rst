Congress Dashboard
==================

Horizon Plugin for Congress

Congress Dashboard is an extension for OpenStack Dashboard that provides a UI
for Congress. With congress-dashboard, a user is able to easily write the
policies and rules for governance of cloud.

* Free software: Apache license
* Source: http://git.openstack.org/cgit/openstack/congress-dashboard
* Bugs: https://bugs.launchpad.net/congress

Enabling in DevStack
--------------------

Add this repo as an external repository into your ``local.conf`` file::

    [[local|localrc]]
    enable_plugin congress https://github.com/openstack/congress

Manual Installation
-------------------

The following below instructions assumes that Horizon is already installed and
its installation folder is <horizon>. Detailed information on how to install
Horizon can be found at https://docs.openstack.org/horizon/latest/contributor/quickstart.html#setup.

The installation folder of Congress Dashboard will be referred to as <congress-dashboard>.

Clone Congress-Dashboard

.. code-block:: console

  $ git clone https://github.com/openstack/congress-dashboard.git
  $ cd congress-dashboard

Install requirements

.. code-block:: console

 $ sudo pip install .

Install Source code

.. code-block:: console

  $ sudo python setup.py install

And enable it in Horizon

.. code-block:: console

  $ ln -s <congress-dashboard>/congress_dashboard/enabled/_50_policy.py <horizon>/openstack_dashboard/local/enabled
  $ ln -s <congress-dashboard>/congress_dashboard/enabled/_60_policies.py <horizon>/openstack_dashboard/local/enabled
  $ ln -s <congress-dashboard>/congress_dashboard/enabled/_70_datasources.py <horizon>/openstack_dashboard/local/enabled
  $ ln -s <congress-dashboard>/congress_dashboard/enabled/_75_monitoring.py <horizon>/openstack_dashboard/local/enabled
  $ ln -s <congress-dashboard>/congress_dashboard/enabled/_80_library.py <horizon>/openstack_dashboard/local/enabled

Restart Apache server

.. code-block:: console

  $ sudo service apache2 restart
