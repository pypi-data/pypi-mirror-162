from setuptools import setup
from auto_preprocess import __version__

with open("README.md", "r") as fh:
    readme = fh.read()

setup(
    name="auto_preprocess",
    version=__version__,
    # url="",
    license="MIT License",
    author="Eduardo M. de Morais",
    long_description="Auto PreProcess package",
    long_description_content_type="text/markdown",
    author_email="emdemor415@gmail.com",
    keywords="",
    description="Auto PreProcess package",
    packages=["auto_preprocess"],
    install_requires=[
        "category-encoders",
        "numpy",
        "optbinning",
        "pandas",
        "PyYAML",
        "scikit-learn",
        "sklearn-pandas",
        "tqdm",
    ],
)
