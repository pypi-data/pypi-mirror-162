[![Tests and type-checks](https://github.com/public-law/new-dale-chall-readability/actions/workflows/python-app.yml/badge.svg)](https://github.com/public-law/new-dale-chall-readability/actions/workflows/python-app.yml) [![Maintainability](https://api.codeclimate.com/v1/badges/ef1198fa2d9246aa3c7d/maintainability)](https://codeclimate.com/github/public-law/new-dale-chall-readability/maintainability) [![PyPI version](https://badge.fury.io/py/new-dale-chall-readability.svg)](https://badge.fury.io/py/new-dale-chall-readability)



# The new Dale-Chall readability formula

I wrote this by ordering a copy of _Readability Revisited: The new Dale-Chall readability formula_. I used the book to code the library from scratch. 


**Installation:**

```bash
$ pip install new-dale-chall-readability
```

**Let's try it out:**

```bash
$ ipython
```

```python
In [1]: from new_dale_chall_readability import cloze_score, reading_level

In [2]: text = (
   ...:     'Latin for "friend of the court." It is advice formally offered '
   ...:     'to the court in a brief filed by an entity interested in, but not '
   ...:     'a party to, the case.'
   ...:     )

In [3]: reading_level(text)
Out[3]: '7-8'

In [4]: cloze_score(text)
Out[4]: 36.91
```

## What's a "cloze score" and "reading level"?

**Cloze** is a deletion test invented by Taylor (1953). The **36.91** score, above, means that roughly that 37% of the words could be deleted and the passage could still be understood. So, a
higher cloze score is more readable. They "range from 58 and above for the easiest passages to 10-15 and below for the most difficult" (Chall & Dale, p. 75).

**Reading level** is the grade level of the material, in years of education. The scale is from
**1** to **16+**.

See the integration test file for text samples from the book, along with their scores. 


## Why yet another Dale-Chall readability library?

It's 2022 and there are probably a half-dozen implementations on PyPI.
So why create another one?

* The existing libraries have issues that made me wonder if the results were accurate. For example:    
  * From my reading, I saw that **reading levels** are a set of
    ten "increasingly broad bands" (p. 75). 
    And they have labels like `3` and `7-8`.
    The existing readability libraries treat these as floating point numbers. 
    But now I believe that an enumeration — or specifically,
    a [Literal](https://docs.python.org/3/library/typing.html#typing.Literal) — captures the formula better:
    `Literal["1", "2", "3", "4", "5-6", "7-8", "9-10", "11-12", "13-15", "16+"]`
  * I also couldn't find a good description of this "new" Dale-Chall formula, and how the
    existing libraries implement it.
  * The readability scores are important for my international dictionary app: 
    It shows definitions sorted with the most readable first, to increase comprehension.
    [The entry for amicus curiae](https://www.public.law/dictionary/entries/amicus-curiae)
    is a good example.
    But I was getting odd results on some pages.
* Use Test-Driven Development to squash bugs and prevent regressions.
* Turn examples from the book into test cases.
* Write with modern Python. I'm no expert, so I'm learning as I go along. E.g., 
  * It passes Pyright strict-mode type-checking.
  * It uses recent type enhancements like `Literal`.
* Present a very easy API to use in any app or library.
  * No need to instantiate an object and learn its API.
  * Just import the needed function and call it.


The result is a library that provides, I think, more accurate readability scores.


## References

Chall, J., & Dale, E. (1995). _Readability revisited: The new Dale-Chall readability formula_.
Brookline Books.

Taylor, W. (1953). _Cloze procedure: a new tool for measuring readability._ Journalism Quarterly, 33, 42-46.
