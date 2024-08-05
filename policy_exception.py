import os
import argparse
import streamlit as st
from dotenv import load_dotenv
from azure.identity import EnvironmentCredential
from azure.mgmt.resource.policy.v2022_06_01 import PolicyClient
from azure.mgmt.resource.policy.v2022_07_01_preview import PolicyClient as pc
from azure.mgmt.resource.policy.v2022_07_01_preview.models import PolicyExemption
from azure_resource_graph_query import run_azure_rg_query
from azure.core.exceptions import HttpResponseError
from pydantic import BaseModel
from common_utils import calculate_expiry


class PolicyAssignmentList(BaseModel):
	display_name : str
	id : str
	policy_definition_id : str
	scope : str

def get_policies(subscription_id: str):
    # Retrieve all policies in the subscription
	credential = EnvironmentCredential()
	client = PolicyClient(credential=credential, subscription_id=subscription_id)
	policy_assignment_list = client.policy_assignments.list()
	return [policy.display_name for policy in policy_assignment_list]

def extract_policy_data(subscription_id: str) -> PolicyAssignmentList:
	"""
	Extract policy details like name, id, assigned by, policy definition id etc from policyInsihts client
	:return:
	"""
	credential = EnvironmentCredential()
	client = PolicyClient(credential=credential, subscription_id=subscription_id)

	policy_assignment_list = client.policy_assignments.list()
	# Extracted polciy details
	policy_extracted_details = []
	for policy in policy_assignment_list:
		extracted_data = {
			'display_name': policy.display_name,
			'id' : policy.id,
			'policy_definition_id' : policy.policy_definition_id,
			'scope' : policy.scope,
		}

		policy_detail = PolicyAssignmentList(**extracted_data)
		policy_extracted_details.append(policy_detail)

	print(f'Total Number of Policy assignments found: {len(policy_extracted_details)}')
	return policy_extracted_details


def verify_policy_is_available(subscription_id:str, policy_name: str):
	"""
	Use azure policyInsight client to verify the provided policy is applied across the specified subscription
	:return:
	"""
	try:

		policy_assignment_list = extract_policy_data(subscription_id=subscription_id)

		policy_to_be_exempted = None
		for policy in policy_assignment_list:
			if policy_name == policy.display_name:
				print(f"Found policy assignment for '{policy_name}' in scope {subscription_id}")
				st.write(f"Found policy assignment for '{policy_name}' in scope {subscription_id}")
				# convert policy obj to dict
				policy_to_be_exempted = policy.__dict__
				break  # Exit the loop once the policy is found
		return policy_to_be_exempted

	except Exception as e:
		print(f"An error occurred while verifying the policy: {e}")
		return None


def create_exemption_for_policy(subscription_id: str, policy_name:str, expires_after:str, unit: str):
	"""
	create policy exemption for mentioned policy
	:param subscription_id:
	:param policy_name:
	:return:
	"""
	credential = EnvironmentCredential()
	client = pc(credential=credential, subscription_id=subscription_id)

	policy_to_be_exempted = verify_policy_is_available(subscription_id=subscription_id, policy_name=policy_name)

	scope = f"/subscriptions/{subscription_id}"
	st.write(f"Scope of exemption is : /subscriptions/{subscription_id}")
	policy_exemption_name = f'exemption for {policy_name}' # <policy name> - <yyyy-<month short form>-<day> HH:MM")>
	print(f'Policy Exemption name will be "{policy_exemption_name}"')
	st.write(f'Policy Exemption name will be "{policy_exemption_name}"')
	expiry_date = calculate_expiry(expires_after=expires_after, unit=unit)
	policy_exemption_description = f'exemption for {policy_name}'

	try:

		parameters = PolicyExemption(
				exemption_category= 'Waiver',
				policy_assignment_id = policy_to_be_exempted['id'],
				expires_on = expiry_date,
				display_name = policy_exemption_name,
				description=policy_exemption_description
			)

		exemption = client.policy_exemptions.create_or_update(scope=scope,policy_exemption_name=policy_exemption_name, parameters=parameters)
		print("Policy exemption created or updated successfully.")
		st.write(f"Policy exemption created or updated successfully. Policy Exemption will expire at {expiry_date}")
		print(f'Policy Exemption will expire at {expiry_date}')

	except HttpResponseError as err:
		# Handle HTTP response errors
		print(f"Failed to create or update policy exemption. Error details: {err}")
		# If available, display the exemption details
		if err.response:
			print("Response details:")
			print(err.response.text)
		return None

	except Exception as e:
		# Handle other exceptions
		print(f"An unexpected error occurred: {e}")
		return None



def main():
	""" Test the code"""
	load_dotenv()

	parser = argparse.ArgumentParser("Automation to provide polci exception in Azure")
	parser.add_argument("--subscription_name", help="Azure subscription to give exemption", required=True, type=str)
	parser.add_argument("--policy_name", help="Policy name to give exemption", required=True, type=str)
	parser.add_argument("--expires_after", help="Policy exemption will epire after", required=False, default=1, type=str)
	parser.add_argument("--unit", help="Unit of time for exemption", type=str, choices=['hour', 'day', 'month'], default='day')

	args = parser.parse_args()

	subscription_name = args.subscription_name
	policy_name = args.policy_name
	expires_after = args.expires_after
	unit = args.unit

	subscription_id = run_azure_rg_query(subscription_name=subscription_name)

	create_exemption_for_policy(subscription_id=subscription_id, policy_name=policy_name, expires_after=expires_after, unit=unit)



if __name__ == "__main__":
	main()