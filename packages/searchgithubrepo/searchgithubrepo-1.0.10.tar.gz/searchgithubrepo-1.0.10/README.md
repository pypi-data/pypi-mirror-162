# Search GitHub repositories
The package searches repositories on GitHub using GraphQL API. One may specify parameters such as programming language, start date, and number of stars to get a *list of GitHub repositories modified on or after the specified start date* and satisfying other filters.

The package takes care of constraints such as API limit and the size of responses by reducing the search scope (in terms of time) by following a mechanism similar to binary search. The search results are stored in a file in the following format per line.

`<repo_owner>/<project name><space><programming language><space><modification date and time>`

Ex: `apache/tomcat Java 2022-08-06T13:31:25Z`

## Parameters
- `--api-token`: GitHub API token or Personal Access Token
- `--out-file`: Output file path
- `--start-date`: Start date for search in dd-mm-yyyy
- `--lang`: Primary programming language of the repositories
- `--min-stars`: Minimum star count 
- `--verbose`: Verbose mode 

## Example
```shell
python3 searchrepo.py --api-token 51ec41929c6f48c23482a734534327d308 --out-file 'repos.csv' --start-date '06-08-2022'
```

Install `searchgithubrepo` package using `pip` and use it in your program.
```python
from searchrepo import search_repo

one_day_old_date = (datetime.datetime.now().date() - datetime.timedelta(days=1))

search_repo(start_date=one_day_old_date,
            out_file='repos.csv',
            api_token='51ec41929c6f48c23482a734534327d308',
            stars=100,
            lang='Java', 
            verbose=True)
```