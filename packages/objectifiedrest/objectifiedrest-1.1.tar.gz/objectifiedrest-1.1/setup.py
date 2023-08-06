from setuptools import setup, find_packages

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="objectifiedrest", 
        version=1.1,
        author="Shahnawaz Akhtar",
        author_email="er.shahnawaz.akhtar@gmail.com",
        description="Wrapper for ORM style access to REST APIs",
        long_description="This package allows to call REST endpoints the way we access objects and object properties. You can also pass parameters to refine the result and authenticate to access private data.",
        packages=find_packages(),
        install_requires=[], # add any additional packages that 
        # needs to be installed along with your package. Eg: 'caer'
        
        keywords=['python', 'rest', 'api', 'rest api', 'orm', 'rest orm', 'easy rest api access'],
        classifiers= []
)