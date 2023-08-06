from setuptools import setup, find_packages
from pathlib import Path

long_description = Path("README.md").read_text()

setup(
    name='pythonConsoleConfigs',
    description="Python Console Configuration",
    long_description=long_description,
    long_description_content_type='text/markdown',
    version='0.9.4',
    license='Apache License',
    author="Stefanos Grigori",
    author_email='gregorystefanos@gmail.com',
    packages=find_packages(),
    url='https://github.com/StefanosGregory/PythonConsoleConfig',
    keywords=['Python', 'Console', 'Configuration', 'Font', 'Color', 'Highlight', 'Style', 'Loading', 'Load']
)
