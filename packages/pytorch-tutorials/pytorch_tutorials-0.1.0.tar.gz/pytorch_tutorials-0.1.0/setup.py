from setuptools import setup, find_packages

setup(
    name='pytorch_tutorials',
    version='0.1.0',    
    description='A resource for learning about PyTorch and deep learning.',
    url='https://github.com/drewbyron/pytorch-tutorials',
    author='William (Drew) Byron',
    author_email='william.andrew.byron@gmail.com',
    license='BSD 2-clause',
    packages=find_packages(),
    install_requires= [
        "ipykernel",
        "pathlib2",
        "numpy>=1.18",
        "pandas>=1.1",
        "scipy>=1.5",
        "pyyaml",
        "matplotlib>=3.3 ",
    ],

    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3.9',
        "Operating System :: OS Independent"
    ],
)