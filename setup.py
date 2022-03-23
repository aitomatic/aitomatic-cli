from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read()

setup(
    name = 'aitomatic',
    version = '0.1.0',
    author = 'Pham Hoang Tuan',
    author_email = 'tuan@aitomatic.com',
    license = 'MIT',
    description = 'aitomatic CLI',
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = 'https://github.com/aitomatic/aitomatic-cli',
    packages = find_packages(),
    install_requires = [requirements],
    python_requires='>=3.7',
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points = '''
        [console_scripts]
        aitomatic=src.aitomatic:aitomatic_cli
    '''
)
