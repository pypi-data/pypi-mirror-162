from setuptools import setup, find_packages

with open('src/flockfysh/requirements.txt', 'r') as f:
    requirements = f.readlines()
  
long_description = open('src/flockfysh/README.md').read()
print(find_packages())

setup(
        name ='flockfysh',
        version ='0.0.1',
        author ='Team Nebula',
        author_email ='teamnebulaco@gmail.com',
        url ='https://github.com/teamnebulaco/flockfysh',
        description ='A data vending machine that gives more than it gets.',
        long_description = long_description,
        long_description_content_type ="text/markdown",
        license ='BSD',
        package_dir={'':'src'},
        packages = find_packages('src'),
        package_data={'': ['default_params/*.yaml']},
        include_package_data=True,
        entry_points ={
            'console_scripts': [
                'flockfysh = flockfysh.run:run'
            ]
        },
        classifiers =[
            "Programming Language :: Python :: 3",
            "Operating System :: OS Independent",
        ],
        keywords ='flockfysh dataset ai web-scraping',
        install_requires = requirements,
        zip_safe = False,
)