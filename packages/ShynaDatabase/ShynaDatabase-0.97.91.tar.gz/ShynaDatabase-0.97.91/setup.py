from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()


setup_args = dict(
     name='ShynaDatabase',
     version='0.97.91',
     packages=find_packages(),
     author="Shivam Sharma",
     author_email="shivamsharma1913@gmail.com",
     description="This package will take care of cleaning the database and querying the database.",
     long_description=long_description,
     long_description_content_type="text/markdown",
    )

install_requires = ['mysql-connector-python', 'ShynaTime', 'ShynaProcess', 'haversine', 'setuptools', 'wheel']

if __name__ == '__main__':
    setup(**setup_args, install_requires=install_requires)
