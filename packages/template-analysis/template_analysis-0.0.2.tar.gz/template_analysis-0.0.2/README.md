# template-analysis

[![Python](https://img.shields.io/pypi/pyversions/template-analysis.svg)](https://badge.fury.io/py/template-analysis)
[![PyPI version](https://img.shields.io/pypi/v/template-analysis.svg)](https://pypi.python.org/pypi/template-analysis/)
[![codecov](https://codecov.io/gh/kitsuyui/template-analysis/branch/main/graph/badge.svg?token=AMEP8YUYXA)](https://codecov.io/gh/kitsuyui/template-analysis)
[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)

Generate template and extract variables from texts.
In other words, template-analysis makes reverse template (untemplate).

## Usage

Currently, this supports to analyze only two texts.

```python
from template_analysis import analyze
result = analyze([
    "A dog is a good pet",
    "A cat is a good pet",
    "A cat is a pretty pet",
    "A bird is a great pet",
])
result.to_format_string()  # => "A {} is a {} pet"
result.args[0]  # => ["dog", "good"]
result.args[1]  # => ["cat", "good"]
result.args[2]  # => ["cat", "pretty"]
result.args[3]  # => ["bird", "great"]
```

## Concepts / Future plans

### Development plans

- [x] 1. Untemplate two texts.
- [x] 2. Untemplate multiple / complex texts.
- [ ] 3. Untemplate nested / tree-structured texts.
- [ ] 4. Support several features for scraping.
- [ ] 5. Implement a more efficient algorithm.

### Image boards

![1-templating](https://user-images.githubusercontent.com/2596972/73120667-7bafbf80-3fb4-11ea-823f-263c0010e0e9.png)
![2-untemplating](https://user-images.githubusercontent.com/2596972/73120668-7bafbf80-3fb4-11ea-9426-5471fcf2e601.png)
![3-template-deriving](https://user-images.githubusercontent.com/2596972/73120669-7bafbf80-3fb4-11ea-8236-1ab68f75ce60.png)
![4-template-deriving-2](https://user-images.githubusercontent.com/2596972/73120670-7c485600-3fb4-11ea-9eba-01aaafd08e4e.png)
![4-automated-scraping](https://user-images.githubusercontent.com/2596972/73120671-7c485600-3fb4-11ea-8ed6-56b93ee99b3a.png)

## License

The 3-Clause BSD License. See also LICENSE file.
