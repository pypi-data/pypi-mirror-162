#!/usr/bin/env python


from distutils.core import setup


setup(
    name="aw_jupyter",
    version="1.10.1",

    install_requires=[
        "jupyterhub>=2.2,<2.3",
        "oauthenticator>=14.2,<14.3",
        "dockerspawner>=12.1,<12.2",
        "python-dotenv>=0.19,<0.20",
        "jupyter_client>=7.3,<8"
    ],
    packages=[
        "aw_jupyter"
    ],
    setup_requires=['wheel']
)