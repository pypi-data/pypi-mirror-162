from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='bluerpc_service',
    packages=find_packages(),
    version='0.0.5',
    author='drosocode',
    license='MIT',
    description='Bluetooth Service for BlueRPC',
    url="https://github.com/BlueRPC/service",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["bleak", "grpcio", "protobuf"],
    python_requires=">=3.7",
    project_urls={
        'Documentation': 'https://bluerpc.github.io/components/workers/service/',
        'Source': 'https://github.com/BlueRPC/service',
    },
    entry_points={
        'console_scripts': [
            'bluerpc_service=bluerpc_service.cli:run'
        ]
    },
)