from setuptools import setup, find_packages

setup(
    name='MolGNN',
    version='0.0.3',
    packages=find_packages(where='MolGNN'),
    url='',
    license='',
    author='Giulio Mattedi',
    author_email='lxu110@stu.suda.edu.cn',
    description='',
    py_modules=['utils'],
    package_dir={'models':'MolGNN/models', 'MolToGraph':'MolGNN/MolToGraph','MolGNN':'utils'}
)
