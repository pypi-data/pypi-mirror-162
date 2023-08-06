from setuptools import setup, find_packages


def requirements():
    with open('requirements.txt') as f:
        return f.read().strip().split('\n')


def version():
    with open('bda3/__version__.py') as f:
        c = f.read()

    d = dict()
    exec(c, d, d)
    return d['__version__']


def readme():
    with open('README.md') as f:
        return f.read()


setup(
    name='bda3',
    version=version(),
    license='MIT',
    description='Algorithms from the book Bayesian Data Analysis by Gelman et. al.',
    long_description=readme(),
    long_description_content_type='text/markdown',
    author='Alexander Dolich',
    author_email='alexander.dolich@kit.edu',
    install_requires=requirements(),
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False
)
