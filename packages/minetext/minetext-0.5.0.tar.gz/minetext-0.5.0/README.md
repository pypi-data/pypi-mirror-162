# minetext

[MINE][2] is a collaboration project between the
[Niedersächsische Staats- und Universitätsbibliothek Göttingen (SUB)][3] and the
[Gesellschaft für wissenschaftliche Datenverarbeitung Göttingen (GWDG)][4] with the goal to offer a convenient platform
for text analysis.

`minetext` is a Python package, which facilitates the interaction between Python clients and the MINE system. For other
clients, [REST API][5] of MINE is the way to go.

**Note**: `minetext` only works on Python version `>=3.7`.

To install it, simply run

```shell
$ pip install minetext
```

## Examples

### Simple search

```python
from minetext import EsRequest, Mine

es_request = EsRequest(search_term='biology')
mine = Mine(es_request)

response = mine.search()

for hit in response:
    print(hit.meta.score, hit.mine.dc_title)
```

The example above shows us how to search in MINE. It is done in 3 steps:

1. Line 3: create an instance of the :ref:`EsRequest <api_esRequest>` class with the query set to ``biology``.
2. Line 4: create an instance of the :ref:`Mine <api_mine>` class. Since all operations are done via this instance,
   creating this instance is the first required step to interact with the MINE system.
3. Line 6: search for the word ``biology`` in MINE. To access the result, simply loop through the ``response``, as shown
   in line 8.

### Get full-text

```python
from minetext import EsRequest, Mine

# Search for all documents which have full-text
es_request = EsRequest(search_term='_exists_:content')

mine = Mine(es_request)
mine.login()

response = mine.search()

for hit in response:
    print(hit.content)
```

To access the full-text, authentication is required. It is done by calling the `login` method of the `Mine` class,
as shown in the example above on line 5. The full-text, if existed, will be accessible via `hit.content`.

The syntax of the `search_term` is the [query string syntax][6].

**Note**: the `response` object is an instance of the `Response` class from the [`elasticsearch-dsl`][7] package

For more information, please refer to the [full documentation][1].

[1]: https://mine.pages-ce.gwdg.de/mine-python/

[2]: https://mine-graph.de/

[3]: https://www.sub.uni-goettingen.de/

[4]: https://www.gwdg.de/

[5]: https://api.mine-graph.de/docs

[6]: https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-query-string-query.html#query-string-syntax

[7]: https://elasticsearch-dsl.readthedocs.io/en/latest/index.html

