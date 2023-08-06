import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="TOMAS",
    version="0.0.1",
    license='MIT',
    author="Qiuyu Lian",
    author_email="qiuyu.lian@sjtu.edu.cn",
    description="A Python Dirichlet Multinomial Mixture Model",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages('tomas'),
    package_dir={'': 'tomas'},
    url="https://github.com/QiuyuLian/TOMAS",
    package_data={
        "": ["clibs/*"],
    },
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