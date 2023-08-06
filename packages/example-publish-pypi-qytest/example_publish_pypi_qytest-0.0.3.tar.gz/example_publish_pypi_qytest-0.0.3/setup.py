import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="example_publish_pypi_qytest",
    version="0.0.3",
    license='MIT',
    author="Qiuyu Lian",
    author_email="qiuyu.lian@sjtu.edu.cn",
    description="example of publishing pypi package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    #url="https://tomas.readthedocs.io/en/latest/",
    #python_requires='>=3.8',
    install_requires=[
        "scikit-learn",

    ]
)
