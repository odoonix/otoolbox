.. These are examples of badges you might want to add to your README:
   please update the URLs accordingly

    .. image:: https://api.cirrus-ci.com/github/<USER>/utils.svg?branch=main
        :alt: Built Status
        :target: https://cirrus-ci.com/github/<USER>/utils
    .. image:: https://readthedocs.org/projects/utils/badge/?version=latest
        :alt: ReadTheDocs
        :target: https://utils.readthedocs.io/en/stable/
    .. image:: https://img.shields.io/coveralls/github/<USER>/utils/main.svg
        :alt: Coveralls
        :target: https://coveralls.io/r/<USER>/utils
    .. image:: https://img.shields.io/pypi/v/utils.svg
        :alt: PyPI-Server
        :target: https://pypi.org/project/utils/
    .. image:: https://img.shields.io/conda/vn/conda-forge/utils.svg
        :alt: Conda-Forge
        :target: https://anaconda.org/conda-forge/utils
    .. image:: https://pepy.tech/badge/utils/month
        :alt: Monthly Downloads
        :target: https://pepy.tech/project/utils
    .. image:: https://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Twitter
        :alt: Twitter
        :target: https://twitter.com/utils

.. image:: https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold
    :alt: Project generated with PyScaffold
    :target: https://pyscaffold.org/

|

otoolbox - Odoo development toolbox 
====================================


    Otoolbox is a tool for managing the Odoo development environment, helping developers work on multiple versions of Odoo simultaneously.


Otoolbox is a specialized tool designed to streamline the management of the Odoo development environment, 
offering significant support to developers who need to handle multiple versions of Odoo at the same time. 
It simplifies the complexities of maintaining and switching between different Odoo instances, which is 
particularly useful for those working on various projects or testing updates across different releases. 
By providing an efficient way to organize and control these environments, Otoolbox enhances productivity 
and ensures that developers can focus on coding and innovation without getting bogged down by setup and 
configuration challenges. This makes it an invaluable asset for anyone involved in Odoo development, 
especially in scenarios requiring simultaneous development or maintenance of multiple Odoo versions.

The Odoo Community Association (OCA) is one of the key groups contributing to the open-source 
development of Odoo, maintaining a variety of repositories tailored to different versions of the 
platform. These repositories contain modules, enhancements, and customizations that enrich Odoo’s 
functionality, making them valuable resources for developers. Otoolbox plays a crucial role in this 
ecosystem by assisting developers in seamlessly integrating these OCA repositories into their development 
environments. This capability allows developers to easily access, manage, and utilize the diverse 
tools and features provided by OCA across multiple Odoo versions, streamlining the process of building 
and testing customized solutions while leveraging the collective efforts of the open-source community.

Visual Studio Code (VS Code) is one of the most widely used tools in software development, valued for 
its flexibility and robust feature set. Otoolbox enhances its utility for Odoo developers by 
automatically generating the necessary configurations to optimize VS Code for Odoo development. 
This includes setting up essential configurations for running and debugging Odoo projects, ensuring 
a smooth and efficient workflow. Additionally, Otoolbox provides features to update and check 
repositories, allowing developers to keep their codebase current and verify the integrity of their 
resources seamlessly within the VS Code environment. By integrating these capabilities, Otoolbox 
simplifies the development process and empowers developers to focus on building high-quality Odoo 
solutions.

Installing OToolbox 
=======================

Installing **OToolbox** is straightforward and requires just a single command. We recommend 
using `pipx`, a tool specifically designed for installing and running Python applications 
in isolated environments.  

Installation Steps
--------------------

To install **OToolbox**, open a terminal and run the following command:  


.. code-block:: bash

    pipx install otoolbox
  

This command ensures that **OToolbox** is installed in a dedicated environment, preventing 
conflicts with other Python packages on your system.  

Why Use `pipx` Instead of Other Methods?
-----------------------------------------

In the past, we supported multiple installation methods, including direct installation via `pip`. 
However, over time, we have streamlined our recommendations. A key reason for this change 
is that **Ubuntu 24 has introduced restrictions on using `pip` for system-wide package installations**. 
These restrictions make traditional `pip install` methods less reliable.  

By using `pipx`, you benefit from:  
✅ **Automatic environment isolation** - Prevents dependency conflicts.  
✅ **Simplified management** - Easily install, upgrade, and uninstall tools.  
✅ **Compatibility with modern Linux distributions** - Works seamlessly on Ubuntu 24 and newer versions.  

For these reasons, we strongly recommend using `pipx` as the preferred method for installing **OToolbox**.


Create New Workspace
====================

To create a workspace using Otoolbox, you first need to set up a dedicated folder for your project. 
For example, you can run the commands `mkdir odoo_workspace_16` to create a folder 
named "odoo_workspace_16" and then `cd odoo_workspace_16` to navigate into it. 


.. code-block:: bash

    mkdir odoo_workspace_16
    cd odoo_workspace_16

Once inside the folder, you can initialize the development environment by executing the 
command `otoolbox run init --odoo-version 16.0`. This single command sets up the entire 
workspace, automatically configuring all the necessary components and dependencies required 
for developing with Odoo version 16.0. 


.. code-block:: bash

    otoolbox run init --odoo-version 16.0
    cd odoo_workspace_16

By doing so, Otoolbox ensures that developers have a 
fully functional environment ready for coding, testing, and debugging, streamlining the 
setup process significantly.







