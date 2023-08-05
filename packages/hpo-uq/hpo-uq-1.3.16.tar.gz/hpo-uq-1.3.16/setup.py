import setuptools

with open('README.rst', 'r') as f:
    long_description = f.read()

setuptools.setup(
    name="hpo-uq",
    version='1.3.16',
    description="Hyperparameter Optimization Tool using Surrogate Modeling and Uncertainty Quantification.",
    long_description=long_description,
    long_description_content_type='text/x-rst',
    scripts = ['bin/hyppo'],
    author="Vincent Dumont",
    author_email="vincentdumont11@gmail.com",
    maintainer="Vincent Dumont",
    maintainer_email="vincentdumont11@gmail.com",
    url="https://hpo-uq.gitlab.io/hyppo",
    license_files = ('LICENSE.txt',),
    packages=setuptools.find_packages(),
    project_urls={
        "Source Code": "https://gitlab.com/hpo-uq/hyppo",
    },
    install_requires=['deap','matplotlib','numpy','pandas','pickle5','plotly','pyyaml','SALib','scipy','sklearn'],
    classifiers=[
        'Intended Audience :: Science/Research',
        "License :: Other/Proprietary License",
        'Natural Language :: English',
        "Operating System :: OS Independent",
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],

)
