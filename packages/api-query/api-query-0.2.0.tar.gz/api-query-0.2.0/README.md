# api-query

A simple tool to query REST APIs with very little boilerplate. For example, to query and print the
title and URL of new stories on HackerNews:

```
GET https://hacker-news.firebaseio.com/v0/newstories.json
[
    -> STORY_ID

    GET https://hacker-news.firebaseio.com/v0/item/{STORY_ID}.json
    { title? -> TITLE, url? -> URL }

    ! print(f'Story {STORY_ID}: {TITLE} ({URL})')
]
```
([examples/hn.query](examples/hn.query))

## Installation

`pip install api-query`

Python 3.10+ is required.

## Usage

```
api-query
    [--max-concurrent 1]
    [--log-level info]
    [--compile-only]
    [--http-rate-limit 1]
    [--http-retry-count 1]
    [--http-base-delay 1.0]
    [--http-max-delay 10.0]
    query-to-run.query
```

`query-to-run.query` should be of the format described in the next section.

`--max-concurrent` specifies the maximum number of concurrently running statements.

`--compile-only` causes the generated Python program to only be printed to stdout, instead of being run.

`--http-rate-limit` is the maximum number of HTTP requests sent per second (on average).

`--http-retry-count` is the maximum number of times HTTP requests will be retried. The time between
retries starts with the value of `--http-base-delay` (in seconds), and follows binary exponential
backoff until it hits `--http-max-delay` (in seconds).

## Query Format

Query files consist of four types of statements:

### Assignment

A line of the form:
```
VAR_NAME = value here
```
assigns `"value here"` to `VAR_NAME`. The value is treated as a Python f-string, so you may write, e.g. `VAR_NAME_1 = {VAR_NAME}.jpg`.

If no value is provided, e.g.
```
PASSWORD =
```
then the environmental variable of the same name is used instead (`$PASSWORD` in this case).

### Python Statement

Python statements can be inserted inline by prefixing them with a `!`. For example,
```
! print('hello')
```

Imports are handled automatically, but can also be specified manually with a Python statement.

### Shell Command

Shell commands can be inserted inline by prefixing them with a `>`. For example,
```
> ls
```

Output of these commands is not captured (and gets mixed into STDOUT), but the command itself is
treated as a f-string, and thus can use variables:
```
> ffmpeg -i {URL} -c copy "{TITLE}.mp4"
```

### HTTP Query

An HTTP query must be of the format:
```
METHOD http://...
- Header1: value (as needed)
...
- Request Body Here (as needed)
Response Handler Here
```

For example, a simple GET query can be done with:
```
GET http://example.com
- User-Agent: value
- Another-HTTP-Header: value
-> EXAMPLE_COM_RESPONSE
```

The URL, as well as the HTTP header values, are converted to f-strings, so you may write, e.g. `- Authorization: Bearer {TOKEN}`.

#### Request Body

The request body must come after all headers, before the response handler, and is optional. There are two options for the request body:

##### String

You can specify the response body as a string. This will be treated as an f-string.

```
- "response_body_here {VAR_NAME}"
```

##### JSON

You can alternatively specify the request body in the following format, which will be encoded and sent as application/json.

```
- {
      field1: "FIELD 1",
      field2: VAR_NAME,
      field3.subfield[0].id: USER_ID,
      field4: [
          { subfield: 3 }
      ]
  }
```
which will be converted into
```
{
    "field1": "FIELD 1",
    "field2": "VALUE OF VAR_NAME HERE",
    "field3": {
        "subfield": [
            { "id": "VALUE OF USER_ID HERE" }
        ]
    },
    "field4": [
        { "subfield": 3 }
    ]
}
```

#### Response Handler

There are two types of ways to handle HTTP responses, similar to the two ways to specify request body.

##### String

You can save the response body as a string to a variable with:
```
-> OUTPUT_VAR
```

##### JSON

You can also deconstruct a JSON response body to only check certain fields and extract certain values. For example:
```
{
    status: 200,
    response: {
        userId: USER_ID,
        documents[0].id -> FIRST_DOCUMENT_ID
    }
}
```
This checks that the response is of the format:
```
{
    "status": 200,
    "response": {
        "userId": "VALUE OF USER_ID HERE",
        "documents": [
            { "id": ..., ... },
            ...
        ],
        ...
    },
    ...
}
```
and saves the value of the first document id to `FIRST_DOCUMENT_ID`.

It is also possible to loop through an array in the response, and do further work, for example:
```
{
    documents: [
        { id -> DOCUMENT_ID }

        GET http://.../{DOCUMENT_ID}
        -> DOCUMENT_CONTENTS

        ! print(DOCUMENT_CONTENTS)
    ]
}
```
This will iterate through every item of the `documents` array in the response, perform a GET request, then print out the response.

For object keys, adding a `?` between the end of the key and the start of the arrow will allow
the key to not exist, in which case the variable is set to `None` instead, e.g.
```
{
    user_id? -> USER_ID
}
```
will set `USER_ID = None` if `user_id` is not a key in the response, instead of throwing an error.

## Example

For examples, please see [the examples directory](examples/).

## Generated Code

To only view the generated code without running, you can run:

```bash
api-query --compile-only file.query
```

or use:
```py
import api_query

generated_code = '\n'.join(api_query.compile(api_query.parse(api_query.lex(query_source))))
```

## License

This utility is licensed under the MIT License.
