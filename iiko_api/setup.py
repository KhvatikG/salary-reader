from setuptools import setup, find_packages

setup(
    name='ki-iiko-api',
    version='0.1',
    packages=find_packages(),
    requirement_path = "requirements.txt",
    install_requires=[
    ],
    author='Хватик Игорь',
    author_email='khvatik.igor@gmail.com',
    description='Библиотека для работы с iikoAPI',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/KhvatikG',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
