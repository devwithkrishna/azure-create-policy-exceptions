import azure.mgmt.resourcegraph as arg
import logging
import streamlit as st
from dotenv import load_dotenv
from azure.identity import EnvironmentCredential


def run_azure_rg_query(subscription_name: str):
    """
    Run a resource graph query to get the subscription id of a subscription back
    :return: subscription_id str
    """
    credential = EnvironmentCredential()
    # Create Azure Resource Graph client and set options
    arg_client = arg.ResourceGraphClient(credential)

    query = f"""
             resourcecontainers 
             | where type == 'microsoft.resources/subscriptions' and name == '{subscription_name}' 
             | project subscriptionId 
            """

    print(f"query is {query}")

    # Create query
    arg_query = arg.models.QueryRequest( query=query)

    # Run query
    arg_result = arg_client.resources(arg_query)

    if not arg_result.data:
        # Handle the case where no subscription ID is found
        st.error(f"No subscription found with the name '{subscription_name}'. Please verify the name and try again.")
        return None
    subscription_id = arg_result.data[0]['subscriptionId']
    print(f"Subscription ID is : {subscription_id}")
    return subscription_id

def main():
    """
    To test the script
    :return:
    """
    load_dotenv()
    logging.info("ARG query being prepared......")
    run_azure_rg_query(subscription_name="TECH-CLOUD-PROD")
    logging.info("ARG query Completed......")


if __name__ == "__main__":
    main()