import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("VERSION", "r") as f:
    version = f.read()

with open('requirements.txt') as f:
    install_requires = f.read().split('\n')

setuptools.setup(
    name="minetext",
    version=version,
    author="Triet Doan",
    author_email="triet.doan@gwdg.de",
    description="Python client for MINE system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab-ce.gwdg.de/mine/mine-python",
    packages=setuptools.find_packages(),
    install_requires=install_requires,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
        "Development Status :: 4 - Beta"
    ],
    python_requires='>=3.7',
)
