from setuptools import setup, find_packages

with open('README.md') as file:
    long_description = file.read()

setup(
    name='alpino-query',
    python_requires='>=3.6, <4',
    version='2.1.5',
    description='Generating XPATH queries based on a Dutch Alpino syntax tree and user-specified token properties.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Digital Humanities Lab, Utrecht University',
    author_email='digitalhumanities@uu.nl',
    url='https://github.com/UUDigitalHumanitieslab/alpino-query',
    license='CC BY-NC-SA 4.0',
    packages=['alpino_query'],
    zip_safe=True,
    install_requires=[
        'lxml'
    ],
    entry_points={
        'console_scripts': [
            'alpino-query = alpino_query.__main__:main'
        ]
    })
