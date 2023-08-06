import pathlib
import setuptools

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setuptools.setup(
    name="motivus",
    version="2.0.0",
    description="Motivus client library",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://motivus.cl",
    author="Motivus SpA",
    author_email="info@motivus.cl",
    license="GPLv3",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["motivus"],
    install_requires=["websockets==8.1", "asyncio==3.4.3", "pyyaml==6.0",
                      "requests==2.26.0", "argparse==1.4.0", "python-dotenv==0.19.2"],
    include_package_data=True,
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'motivus=motivus.cli:CLI'
        ]
    }
)
