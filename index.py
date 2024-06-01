from datetime import datetime, timedelta
import time
import boto3


ce_client = boto3.client("ce")


def lambda_handler(event, context):
    try:
        # List inactive tags
        tag_list = []
        response = ce_client.list_cost_allocation_tags(
            Status="Inactive",
            MaxResults=10,
        )
        tag_list.extend([tag["TagKey"] for tag in response["CostAllocationTags"]])
        while "NextToken" in response:
            response = ce_client.list_cost_allocation_tags(
                Status="Inactive",
                MaxResults=10,
                NextToken=response["NextToken"],
            )
            tag_list.extend([tag["TagKey"] for tag in response["CostAllocationTags"]])

        print(f"The following tags are inactive: {tag_list}")
        print(f"Activate 【{len(tag_list)}】tags as cost allocation tags.")

        # Activate tags as cost allocation tags
        if len(tag_list) > 0:
            for tag in tag_list:
                response = ce_client.update_cost_allocation_tags_status(
                    CostAllocationTagsStatus=[
                        {
                            "TagKey": tag,
                            "Status": "Active",
                        },
                    ]
                )
                # Caution LimitExceededException
                time.sleep(1)
            print(f"Cost allocation tag activation processing completed.")

        # Start Backfill
        today = datetime.now()
        one_year_ago = today - timedelta(days=365)
        one_year_ago = one_year_ago.strftime("%Y-%m-%d")
        print(f"Start backfill from {one_year_ago}.")
        response = ce_client.start_cost_allocation_tag_backfill(
            BackfillFrom=one_year_ago,
        )

    except Exception as e:
        print(f"An error has occurred: {e}")
