from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup_args = dict(
    name='ShynaAutomation',
    version='0.1.38',
    packages=find_packages(),
    author="Shivam Sharma",
    author_email="shivamsharma1913@gmail.com",
    description="Shyna Backend Functionality Package For Automation",
    long_description=long_description,
    long_description_content_type="text/markdown",
)

install_requires = ['ShynaTime', 'ShynaDatabase', 'ShynaProcess', 'imbox', 'beautifulsoup4', 'mysql-connector-python', 'nltk', 'setuptools', 'wheel']

if __name__ == '__main__':
    setup(**setup_args, install_requires=install_requires)
