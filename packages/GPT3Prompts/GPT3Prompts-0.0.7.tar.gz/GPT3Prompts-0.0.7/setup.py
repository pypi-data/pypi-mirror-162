import setuptools
from setuptools import setup, find_packages
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="GPT3Prompts", # Replace with your own username
    version="0.0.7",
    license='MIT',
    author="Falahgs.G.Saleih",
    author_email="falahgs07@gmail.com",
    description="GPT3 For Generator any Prompts AI Art Module ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/falahgs/",
    packages=find_packages(),
    keywords = ['GPT-3', 'AI Art','Artificial Intelligence ','artist'],   # Keywords that define your package best
    install_requires=[ 'openai'],
    classifiers=["Programming Language :: Python :: 3","License :: OSI Approved :: MIT License","Operating System :: OS Independent",],
    python_requires='>=3.6',)