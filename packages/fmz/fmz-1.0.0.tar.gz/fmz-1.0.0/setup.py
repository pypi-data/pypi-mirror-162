from setuptools import setup

setup(
    name="fmz",
    version = "1.0.0",
    python_requires='>=3.6.0',
    author='fu-mingzhe',
    author_email='2372769798@qq.com',
    packages=["fmz_multi_function"],
    install_requires=[
        "requests",
        "tqdm",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
