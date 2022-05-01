from setuptools import setup, find_packages


setup(
    name="bookmark",
    version="0.6.0",
    # py_modules=["bookmark"],
    package_dir={"": "src"},
    packages=find_packages("bookmark"),
    include_package_data=True,
    install_requires=["rich-click", "getkey", "rich"],
    entry_points={"console_scripts": ["bm = bookmark.scripts.cli:cli"]},
)
