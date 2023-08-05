import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='CompassAI',
    version='0.0.1',
    author='Jirapat Samranvedhya',
    author_email='jirapat.samranvedhya@optum.com',
    description='For evaluating trained model by bootstrapping test set, assessing fairness, and model card',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/optum-labs/CompassAI',
    license='MIT',
    packages=['CompassAI'],
    install_requires=['joblib', 'sklearn', 'seaborn', 'fairlearn', 'pip==22.0.4', 'model-card-toolkit', 'interpret-community', ], #'httplib2==0.20.2'
)
