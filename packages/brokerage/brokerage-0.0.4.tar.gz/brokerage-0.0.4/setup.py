from setuptools import setup

def readme():
    with open("README.md") as f:
        return f.read()

setup(
    name="brokerage",
    version="0.0.1",
    description="Simulate data feed from brokerage",
    long_description=readme(),
    logn_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: Unstable",
        "License :: MIT License",
        "Programming Language :: Python 3.10",
        "Operating System :: OS Independent",
    ],
    url="https://github.com/yongkheng/brokerage",
    author="Goh Yong Kheng",
    author_email="goh.yongkheng@gmail.com",
    keywords="finance",
    license="MIT",
    packages=["brokerage", ],
    install_requires=[],
    include_package_data=True,
)
