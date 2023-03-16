import logging
import pprint
import sys
import time
from uuid import UUID

from azure.core.exceptions import HttpResponseError
from azure.identity import DefaultAzureCredential
from azure.mgmt.consumption import ConsumptionManagementClient

pp = pprint.PrettyPrinter(indent=4)


def main():
    mgmt_group = sys.argv[1]
    run(mgmt_group)


def run(mgmt_group):

    credentials = DefaultAzureCredential(exclude_shared_token_cache_credential=True)

    # It doesn't matter which subscription ID we use for this bit.
    consumption_client = ConsumptionManagementClient(
        credential=credentials, subscription_id=str(UUID(int=0))
    )
    usage_details = consumption_client.usage_details.list(
        scope=f"/providers/Microsoft.Management/managementGroups/{mgmt_group}"
    )

    data = []
    i = 0
    start = time.perf_counter()
    try:
        for usage_detail in usage_details:
            i += 1
            if i % 1000 == 0:
                duration = time.perf_counter()-start
                print(f"got {i}th item in {duration}")

            data.append(usage_detail)
    except HttpResponseError as e:
        logging.exception(e)
        pp.pprint(e.response.headers)


if __name__ == '__main__':
    main()

