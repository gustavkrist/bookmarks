from setuptools import setup, find_packages


setup(
    name="bookmark",
    version="0.1.0",
    # py_modules=["bookmark"],
    packages=find_packages(),
    include_package_data=True,
    install_requires=["click", "getkey", "rich"],
    entry_points={"console_scripts": ["bm = bookmark:cli"]},
)
