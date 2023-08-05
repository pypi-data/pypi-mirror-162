import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='CompassAI',
    version='0.0.3',
    author='Jirapat Samranvedhya',
    author_email='jirapat.samranvedhya@optum.com',
    description='For evaluating trained model by bootstrapping test set, assessing fairness, and model card',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/optum-labs/CompassAI',
    license='MIT',
    packages=['CompassAI'],
    install_requires=['joblib==0.14', 'sklearn==0.0', 'seaborn==0.11.2', 'fairlearn==0.7.0', 'pip==22.0.4', 'interpret-community==0.24.1', ], #'httplib2==0.20.2'
)
