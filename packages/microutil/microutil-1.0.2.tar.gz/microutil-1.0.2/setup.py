import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="microutil",
    version="1.0.2",
    author="sunshine",
    author_email="firstsoft@163.com",
    description="基于django框架集成zookeeper分布式微服务的服务注册与发现工具包，方便HTTP远程调用",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/autohawkeye/microutil.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['kazoo==2.5.0', 'lz4>=4.0.1', 'six>=1.16.0'],
    python_requires='>=3'
)