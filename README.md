# Consumption Client Rate Limiting - Minimal Reproducible Example

Azure subscription usage data can be obtained with a `ConsumptionManagementClient`.
If there is a lot of usage data to retrieve, you will eventually get an exception:

```text
azure.core.exceptions.HttpResponseError: (429) Too many requests. Please retry after 60 seconds.
```

There is [a page](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/request-limits-and-throttling#subscription-and-tenant-limits)
in the docs about limits and throttling but the numbers mentioned don't seem to match the number of requests I can make before an error occurs.
If the tenant and subscription level limits are 12,000/hour, does that mean that they "regenerate" at a rate of 200/minute?

There are also some fields in the response headers but the remaining-request fields also do not match what I can request in practice.

## Installing

1. Install Poetry
2. Clone the repo
2. Install with `poetry install`
3. Activate a shell with `poetry shell`

## Running

1. With your Poetry shell activated, run `mre "name-of-your-management-group"` in the terminal, or
2. In a Python prompy, call `mre.main.run("name-of-your-management-group")`
3. After some number (typically 10k-20k) of usage details have been retrieved, an `HttpResponseError` will be raised.

## Observations

The HTTPResponseError arises from here: <https://github.com/Azure/azure-sdk-for-python/blob/c10f9d9bf3cc3c451786cf2bb8da38815ded1598/sdk/core/azure-core/azure/core/paging.py#L76>

By placing the following in the `get_next()` function of the `UsageDetailsOperations` class, 

```python
print(
    "x-ms-ratelimit-remaining-tenant-reads",
    response.headers.get("x-ms-ratelimit-remaining-tenant-reads")
)
print(
    "x-ms-ratelimit-remaining-microsoft.consumption-commercial-requests",
    response.headers.get("x-ms-ratelimit-remaining-microsoft.consumption-commercial-requests")
)
```
we can observe that both of these counters decrease:

- `'x-ms-ratelimit-remaining-microsoft.consumption-commercial-requests': '0'`
- `'x-ms-ratelimit-remaining-tenant-reads': '11999'`

However, `x-ms-ratelimit-remaining-microsoft.consumption-commercial-requests` resets to `5` a number of times, so doesn't seem to be the root cause of the error.

The full output and traceback is 

> x-ms-ratelimit-remaining-tenant-reads 11999
x-ms-ratelimit-remaining-microsoft.consumption-commercial-requests 4
got 1000th item in 4.699002401001053
x-ms-ratelimit-remaining-tenant-reads 11998
x-ms-ratelimit-remaining-microsoft.consumption-commercial-requests 3
got 2000th item in 7.167858090004302
x-ms-ratelimit-remaining-tenant-reads 11997
x-ms-ratelimit-remaining-microsoft.consumption-commercial-requests 2
got 3000th item in 9.412916931993095
x-ms-ratelimit-remaining-tenant-reads 11996
x-ms-ratelimit-remaining-microsoft.consumption-commercial-requests 1
got 4000th item in 11.778902984995511
x-ms-ratelimit-remaining-tenant-reads 11995
x-ms-ratelimit-remaining-microsoft.consumption-commercial-requests 0
got 5000th item in 14.213970733006136
x-ms-ratelimit-remaining-tenant-reads 11993
x-ms-ratelimit-remaining-microsoft.consumption-commercial-requests 5
got 6000th item in 21.28194115399674
x-ms-ratelimit-remaining-tenant-reads 11992
x-ms-ratelimit-remaining-microsoft.consumption-commercial-requests 4
got 7000th item in 23.948645091993967
x-ms-ratelimit-remaining-tenant-reads 11991
x-ms-ratelimit-remaining-microsoft.consumption-commercial-requests 3
got 8000th item in 27.537610008992488
x-ms-ratelimit-remaining-tenant-reads 11990
x-ms-ratelimit-remaining-microsoft.consumption-commercial-requests 2
got 9000th item in 30.667021379005746
x-ms-ratelimit-remaining-tenant-reads 11989
x-ms-ratelimit-remaining-microsoft.consumption-commercial-requests 1
got 10000th item in 33.505736774997786
x-ms-ratelimit-remaining-tenant-reads 11988
x-ms-ratelimit-remaining-microsoft.consumption-commercial-requests 0
got 11000th item in 37.52532706200145
x-ms-ratelimit-remaining-tenant-reads 11999
x-ms-ratelimit-remaining-microsoft.consumption-commercial-requests 5
got 12000th item in 40.663161592994584
x-ms-ratelimit-remaining-tenant-reads 11998
x-ms-ratelimit-remaining-microsoft.consumption-commercial-requests 4
got 13000th item in 42.96654611699341
x-ms-ratelimit-remaining-tenant-reads 11997
x-ms-ratelimit-remaining-microsoft.consumption-commercial-requests 3
got 14000th item in 45.25793475100363
x-ms-ratelimit-remaining-tenant-reads 11996
x-ms-ratelimit-remaining-microsoft.consumption-commercial-requests 2
got 15000th item in 47.612254331994336
x-ms-ratelimit-remaining-tenant-reads 11995
x-ms-ratelimit-remaining-microsoft.consumption-commercial-requests 1
got 16000th item in 49.768035707005765
x-ms-ratelimit-remaining-tenant-reads 11994
x-ms-ratelimit-remaining-microsoft.consumption-commercial-requests 0
got 17000th item in 52.005142801004695
x-ms-ratelimit-remaining-tenant-reads 11999
x-ms-ratelimit-remaining-microsoft.consumption-commercial-requests 0
ERROR:root:(429) Too many requests. Please retry after 60 seconds.
Code: 429
Message: Too many requests. Please retry after 60 seconds.
Traceback (most recent call last):
  File "redacted", line 32, in run
    for usage_detail in usage_details:
  File "redacted", line 132, in __next__
    return next(self._page_iterator)
  File "redacted", line 76, in __next__
    self._response = self._get_next(self.continuation_token)
  File "redacted", line 239, in get_next
    raise HttpResponseError(response=response, model=error, error_format=ARMErrorFormat)
azure.core.exceptions.HttpResponseError: (429) Too many requests. Please retry after 60 seconds.
Code: 429
Message: Too many requests. Please retry after 60 seconds.
ERROR:root:{
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache',
    'Content-Length': '86',
    'Content-Type': 'application/json; odata.metadata=none',
    'Expires': '-1',
    'session-id': 'redacted',
    'x-ms-request-id': 'redacted',
    'x-ms-ratelimit-microsoft.consumption-commercial-retry-after': '60',
    'x-ms-ratelimit-remaining-microsoft.consumption-commercial-requests': '0',
    'OData-Version': '4.0',
    'X-Powered-By': 'ASP.NET',
    'x-ms-ratelimit-remaining-tenant-reads': '11999',
    'x-ms-correlation-request-id': 'redacted',
    'x-ms-routing-request-id': 'redacted',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    'X-Content-Type-Options': 'nosniff',
    'Date': 'Thu, 16 Mar 2023 11:53:01 GMT',
    'Connection': 'close'
}
