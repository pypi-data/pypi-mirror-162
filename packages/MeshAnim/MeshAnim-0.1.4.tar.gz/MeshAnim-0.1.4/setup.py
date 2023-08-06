import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="MeshAnim",
    version="0.1.004",
    author="Gaetan Desrues",
    author_email="gaetan.desrues@inria.fr",
    description="Meshes animations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.inria.fr/gdesrues1/MeshAnim",
    packages=["MeshAnim"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
