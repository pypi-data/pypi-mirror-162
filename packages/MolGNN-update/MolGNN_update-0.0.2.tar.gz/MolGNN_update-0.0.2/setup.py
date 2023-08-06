from setuptools import setup, find_packages

setup(
    name='MolGNN_update',
    version='0.0.2',
    packages=find_packages(),
    url='',
    license='MIT License',
    author='Giulio Mattedi',
    author_email='lxu110@stu.suda.edu.cn',
    description='',
    python_requires='>=3.5, <=3.8',
    install_requires=['rdkit', 'torch', 'numpy', 'torch-geometric', 'torch-scatter', 'torch-sparse']
)
