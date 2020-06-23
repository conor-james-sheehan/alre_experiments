from setuptools import setup

setup(
    name='alre_experiments',
    version='0.1',
    packages=['util', 'experiments', 'experiments.mixtures_parameterized'],
    url='github.com/cjs220/alre_experiments',
    license='MIT',
    author='Conor Sheehan',
    author_email='conor.sheehan-2@manchester.ac.uk',
    description='',
    install_requires=['matplotlib', 'pandas', 'numpy', 'joblib', 'PyYAML', 'scipy', 'tensorflow',
                      'active_learning_ratio_estimation'],
    include_package_data=True
)
