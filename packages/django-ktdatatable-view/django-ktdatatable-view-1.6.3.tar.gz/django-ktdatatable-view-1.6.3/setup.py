import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="django-ktdatatable-view",
    version="1.6.3",
    author="Longbowou",
    author_email="blandedaniel@gmail.com",
    description="Django KTDatatable View",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/longbowou/django-ktdatatable-view",
    project_urls={
        "Bug Tracker": "https://gitlab.com/longbowou/django-ktdatatable-view/-/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
