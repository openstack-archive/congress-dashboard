===============================
Congress Dashboard
===============================

Horizon Plugin for Congress

* Free software: Apache license
* Source: http://git.openstack.org/cgit/openstack/congress-dashboard
* Bugs: http://bugs.launchpad.net/congress

Features
--------

* TODO

Enabling in DevStack
--------------------

Add this repo as an external repository into your ``local.conf`` file::

    [[local|localrc]]
    enable_plugin congress https://github.com/openstack/congress

Manual Installation
-------------------

Begin by cloning the Horizon and Congress Dashboard repositories::

    git clone https://github.com/openstack/horizon
    git clone https://github.com/openstack/congress-dashboard

Create a virtual environment and install Horizon dependencies::

    cd horizon
    python tools/install_venv.py

Set up your ``local_settings.py`` file::

    cp openstack_dashboard/local/local_settings.py.example openstack_dashboard/local/local_settings.py

Open up the copied ``local_settings.py`` file in your preferred text
editor. You will want to customize several settings:

-  ``OPENSTACK_HOST`` should be configured with the hostname of your
   OpenStack server. Verify that the ``OPENSTACK_KEYSTONE_URL`` and
   ``OPENSTACK_KEYSTONE_DEFAULT_ROLE`` settings are correct for your
   environment. (They should be correct unless you modified your
   OpenStack server to change them.)

Install Congress Dashboard with all dependencies in your virtual environment::

    tools/with_venv.sh pip install -e ../congress-dashboard/

And enable it in Horizon::

    ln -s ../congress-dashboard/congress_dashboard/enabled/_50_policy.py openstack_dashboard/local/enabled
    ln -s ../congress-dashboard/congress_dashboard/enabled/_60_policies.py openstack_dashboard/local/enabled
    ln -s ../congress-dashboard/congress_dashboard/enabled/_70_datasources.py openstack_dashboard/local/enabled

To run horizon with the newly enabled Congress Dashboard plugin run::

    ./run_tests.sh --runserver 0.0.0.0:8080

to have the application start on port 8080 and the horizon dashboard will be
ayvailable in your browser at http://localhost:8080/
