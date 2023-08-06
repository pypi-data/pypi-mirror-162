import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="tomas",
    version="0.0.3",
    license='MIT',
    author="Qiuyu Lian",
    author_email="qiuyu.lian@sjtu.edu.cn",
    description="A tool for TOtal-MRNA-Aware Single-cell RNA-seq data analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages('tomas'),
    package_dir={'': 'tomas'},
    url="https://tomas.readthedocs.io/en/latest/",
    python_requires='>=3.8',
    install_requires=[
        "pyDIMM==0.0.2",
        "numpy",
        "scipy",
        "tqdm",
        "multiprocessing",
        "scanpy",
        "pickle",
        "statsmodels"
    ]
)