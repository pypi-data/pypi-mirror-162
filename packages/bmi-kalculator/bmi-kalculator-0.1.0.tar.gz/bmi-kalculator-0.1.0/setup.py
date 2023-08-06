from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

VERSION = '0.1.0'

setup(
    name='bmi-kalculator',
    version=VERSION,
    packages=['bmi_kalculator'],  # or use find_packages()
    url='https://github.com/donwany',
    license='LICENSE.txt',
    author='Theophilus Siameh',
    author_email='theodondre@gmail.com',
    description='Calculates body mas index (BMI) based on a given set of parameters such as weight, height, gender, age and life-style',
    long_description=long_description,  # open('README.md').read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    install_requires=[],
    keywords=['python', 'bmi', 'bmi calculator']
)
