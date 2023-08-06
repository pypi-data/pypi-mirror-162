import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="code-attention-visualizer",
    version="0.0.4",
    author="Matteo Paltenghi",
    author_email="mattepalte@live.it",
    description="Visualizer for human attention over source code tokens.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MattePalte/codeattention",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=["codeattention"],
    python_requires=">=3.6",
    install_requires=[
        "numpy",
        "matplotlib",
        "javalang",
        "asttokens",
        "setuptools",
        "Pillow"
    ],
    include_package_data=True
)
