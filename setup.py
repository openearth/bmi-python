from setuptools import setup, find_packages
import sys

version = '0.2.7'

long_description = '\n\n'.join([
    open('README.rst').read(),
    open('CREDITS.rst').read(),
    open('CHANGES.rst').read(),
])

install_requires = [
    'setuptools',
    'numpy',
    #    'pandas',
    #    'psutil',
    'docopts',
    'six',
    # 2.2.1 is broken: https://github.com/laysakura/rainbow_logging_handler/issues/7
    #    'rainbow_logging_handler<2.2.1'
]

if sys.version_info[0] < 3:
    install_requires.append('faulthandler')

tests_require = [
    'nose',
    'mock',
    'coverage'
]

setup(
    name="bmi-python",
    version=version,
    description="Python wrapper for BMI libraries",
    long_description=long_description,
    # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries",
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5'
    ],
    keywords=["hydrodynamic", "simulation", "flooding", "BMI"],
    author='Fedor Baart',
    author_email='fedor.baart@deltares.nl',
    url='https://github.com/openearth/bmi-python',
    license='GPLv3+',
    packages=find_packages(exclude=["contrib", "docs", "tests*"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    #    setup_requires=[
    #        'sphinx',
    #        'sphinx_rtd_theme'
    #    ],

    tests_require=tests_require,
    extras_require={'test': tests_require},
    test_suite='nose.collector',
    entry_points={'console_scripts': [
        '{0} = bmi.runner:main'.format(
            'bmi-runner')
    ]}
)
