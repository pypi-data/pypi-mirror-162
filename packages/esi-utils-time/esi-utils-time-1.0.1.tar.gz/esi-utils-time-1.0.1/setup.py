from distutils.core import setup
import os

setup(
    name="esi-utils-time",
    version="1.0.1",
    description="USGS Earthquake Impact Utilities",
    author="Mike Hearne",
    author_email="mhearne@usgs.gov",
    url="https://code.usgs.gov/ghsc/esi/esi-utils-time",
    packages=[
        "esi_utils_time",
    ],
    package_data={
        "esi_utils_time": [
            os.path.join("data", "*"),
        ]
    },
)
