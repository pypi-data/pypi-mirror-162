import setuptools

setuptools.setup(
    name='fscloudutils',
    packages=['fscloudutils'],
    version='1.0.38',
    license='MIT',
    python_requires='>=3.6',
    description="A package for all fs cloud utilities",
    author="Yotam Raz, Maayan Shriki",
    install_requires=["scikit-image", "pillow", "requests", "boto3", "pandas"]  # mysql-connector-python
)
