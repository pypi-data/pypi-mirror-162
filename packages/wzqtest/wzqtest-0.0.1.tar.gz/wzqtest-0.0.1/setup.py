from setuptools import setup

setup(
    name='wzqtest',
    version='0.0.1',
    python_requires='>=3.6.0',
    author='wzq',
    author_email='wangwood817@gmail.com',
    url='https://editst.com',
    description='Example Python Package',
    long_description=r'**Example Python Package**',
    long_description_content_type='text/markdown',
    packages=['wzqtest'],
    entry_points={
    'console_scripts': ['example=example:main'],
    },
    install_requires=[],
    classifiers=[
    'License :: OSI Approved :: MIT License',

    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    ],
)
