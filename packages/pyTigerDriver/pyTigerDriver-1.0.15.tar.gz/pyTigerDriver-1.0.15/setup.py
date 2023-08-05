import setuptools

with open("README.md", "r") as rdm:
    desc = rdm.read()

setuptools.setup(
    name="pyTigerDriver",
    version="v1.0.15",
    author="TigerGraph Inc.",
    author_email="support@tigergraph.com",
    description="GSQL client for TigerGraph",
    long_description=desc,
    license='Apache 2',
    long_description_content_type="text/markdown",
    keywords=['gsql', 'client','tigergraph'],
    requires=["requests"],
    url="https://github.com/tigergraph/pyTigerDriver",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3",
        'License :: OSI Approved :: Apache Software License',
        "Operating System :: OS Independent",
        "Topic :: Database",
    ],
    python_requires='>=3.5'
)
