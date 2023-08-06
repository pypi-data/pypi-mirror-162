# author: Drew Botwinick, Botwinick Innovations
# license: 3-clause BSD
import setuptools

with open("README.md", 'r') as f:
    readme_txt = f.read()

setuptools.setup(
    name="vpd",
    version="0.9.3",
    author="Drew Botwinick",
    author_email="foss@drewbotwinick.com",
    description="VirtualPathDictChains. Hierarchical, Addressable Dicts, potentially using YaML",
    long_description=readme_txt,
    long_description_content_type="text/markdown",
    url="https://github.com/dbotwinick/python-vpd",
    packages=setuptools.find_packages(),
    install_requires=['six', 'PyYAML'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: BSD License',
        "Operating System :: OS Independent",
    ],
    python_requires='>=2.7, >=3.6',
)
