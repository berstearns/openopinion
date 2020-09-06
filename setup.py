import setuptools

with open("README.md") as fh:
    long_description = fh.read()

setuptools.setup(
        name="igscraper",
        version="0.0.1",
        author="Bernardo",
        author_email="bernardo.stearns@gmail.com",
        description="IG scraper",
        long_description=long_description,
        long_description_content_type="text/markdown",
        classifiers=[
            "Programming Language :: Python :: 3",
            "Operating System :: OS Independent",
            ],
        python_requires='>=3.6',
        packages=setuptools.find_packages('src'),
        package_dir = {'':'src'},
        include_package_data=True,
        data_files=[('', ['src/igscraper/collect_comments.js'])]
        )
