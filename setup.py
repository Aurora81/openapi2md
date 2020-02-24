from setuptools import setup

setup(
    name='openapi2md',
    license='Apache License 2.0',
    packages=['openapi2md'],
    version='0.3',
    description='Generate Markdown documentation from OpenAPI 3 definition',
    author='Aurora81',
    url='https://github.com/Aurora81/openapi2md',
    scripts=['cmd/openapi2md'],
    keywords=['openapi', 'documentation', 'markdown', 'docx'],
    install_requires=['PyYAML', 'future', 'yamlordereddictloader'],
    python_requires='>=2.7, <4',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache License 2.0',
        'Programming Language :: Python :: 3'
    ]
)