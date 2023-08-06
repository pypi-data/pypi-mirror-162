from setuptools import setup, find_packages
import pathlib

## Template from https://github.com/pypa/sampleproject/blob/main/setup.py

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")


setup(
    name="biasgen",
    version="0.1.0",
    description="Utility functions to produce and visualize simulated "
                "bias fields generated according to Kern et. al's "
                "sinusoidal sensitivity model.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lucianoAvinas/biasgen",
    author="Luciano Vinas",
    author_email="lucianovinas@g.ucla.edu",
    license='MIT',
    packages=find_packages(where="biasgen"),
    python_requires=">=3.10",
    install_requires=[
        "numpy>=1.20",
        "scipy",
        "matplotlib"
    ],
    extras_require={"gpu": ["cupy-cuda11x"]
    },
)