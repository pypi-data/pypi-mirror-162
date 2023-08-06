from distutils.core import setup

setup(
    name="job_helper",
    version="0.1.10",
    description="Job helper to use with the job api",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
    ],
    author="Matthias Dillen",
    author_email="matthias.dillen@inuits.eu",
    license="GPLv2",
    packages=["job_helper"],
    provides=["job_helper"],
)
