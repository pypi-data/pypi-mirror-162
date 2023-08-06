import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
   long_description = fh.read()

install_requires = [
   "requests",
   "jwt",
   "Click",
   "tqdm",
   "ipywidgets"
]

"""scripts=[
   "bin/stochasticx"
]"""

setuptools.setup(
   name='stochasticx',
   version='0.0.1',
   author='Marcos Rivera Martínez, Sarthak Langde, Glenn Ko, Subhash G N, Jolina Li',
   author_email='marcos.rm@stochastic.ai, sarthak.langde@stochastic.ai, glenn@stochastic.ai, subhash.gn@stochastic.ai, jolina.li@mail.utoronto.ca',
   description='Stochastic client library',
   long_description=long_description,
   long_description_content_type="text/markdown",
   url="https://github.com/stochasticai/stochasticx",
   classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
   ],
   package_dir={"": "src"},
   packages=setuptools.find_packages(where="src"),
   python_requires=">=3.7",
   install_requires=install_requires,
   entry_points='''
      [console_scripts]
      stochasticx=stochasticx.scripts.stochasticx:cli
   ''', 
)