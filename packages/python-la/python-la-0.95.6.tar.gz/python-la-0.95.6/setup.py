from setuptools import setup, find_packages
import codecs
import os


VERSION = '0.95.6'
DESCRIPTION = 'Python linear algebra liabrary'
LONG_DESCRIPTION = """
# python-la : Python linear algebra
## introduction
The aim of this project is to implement programatically all of the mathematical operations you can in linear algebra, and more so - to implement themt in such a way that it will be written programmatically as close to mathematically as possible

## How to install
```pip install python-la```
## Examples
```python
>> from python_la import Matrix, Span, Vector, PolynomialSimple, LinearMap, RealField, VectorSpace

>> Matrix([[1,2],[3,4]]).gaussian_elimination())
---------
| 1 | 0 |
---------
| 0 | 1 |
---------

>> Matrix([[1, 2, 3], [4, 5, 6], [7, 8, 9]]).characteristic_polynomial
X^3 - 15X^2 - 18X

>> Matrix([[1, 0, 1],[0, 1, 1]]).kernel
[-1, -1, 1]

>> v1, v2 = Vector([3, 4]), Vector([4, 5])
>> Span([v1,v2]).toOrthonormal()
[0.6, 0.8]
[0.8, -0.6]

>> R2 = RealField(2)
>> src_field, dst_field = R2, R2
>> lm = LinearMap(src_field, dst_field, lambda vector, result_field: Vector([field.zero, vector[0]], result_field))
>> x_squared = PolynomialSimple.fromString("x^2")
>> plus_1 = PolynomialSimple.fromString("x+1")
>> v = VectorSpace(R2).random()
>> P = plus_1(x_squared)
>> P
X^2 + 1
>> P(lt)(v) == v
True
```
## Example
"""

setup(
    name="python-la",
    version=VERSION,
    author="danielnachumdev (Daniel Nachum)",
    author_email="<danielnachumdev@gmail.com>",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'linear algebra', 'vector', 'matrix',
              'field', 'vector field', 'span', 'linear maps', 'bilinear form', 'inner product', 'linear transformation'],
    classifiers=[
        # "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
