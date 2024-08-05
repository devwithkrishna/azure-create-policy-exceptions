import streamlit as st
from dotenv import load_dotenv
from policy_exception import create_exemption_for_policy, get_policies
from azure_resource_graph_query import run_azure_rg_query


def main():
	"""run streamlit app"""
	load_dotenv()
	st.header("Azure Policy Exemption Tool", divider='rainbow')
	subscription_name = st.text_input("Enter Subscription Name")
	if subscription_name:
		st.session_state.subscription_name = subscription_name
		subscription_id = run_azure_rg_query(subscription_name=subscription_name)
		st.session_state.subscription_id = subscription_id
		st.success(f"Subscription ID of {subscription_name}: {subscription_id}")
	else:
		st.error(f"Subscription {subscription_name} not found")
	if subscription_id:
	# if 'subscription_id' in st.session_state:
		policies = get_policies(subscription_id=subscription_id)
		selected_policy = st.selectbox("Select a Policy", policies)
		if selected_policy:
			st.write(f"You selected: {selected_policy}")
			st.session_state.selected_policy = selected_policy

		expires_after = st.text_input("Policy Will Expires After")
		unit = st.selectbox("Unit", ["hour", "day", "month"])

		# Print the exemption period
		st.write(f"Policy exemption will expire after {expires_after} {unit}")

		# Run streamlit app by clicking submit
		if st.button("Apply Exemption"):
			# call policy exemption creation function
			create_exemption_for_policy(subscription_id=subscription_id, policy_name=selected_policy,
										expires_after=expires_after, unit=unit)



if __name__ == "__main__":
	main()
