import streamlit as st
import os
from streamlit_msal import Msal
from dotenv import load_dotenv
from policy_exception import create_exemption_for_policy, get_policies
from azure_resource_graph_query import run_azure_rg_query

load_dotenv()
# Replace with your Azure AD app details
client_id = os.getenv('STREAMLIT_CLIENT_ID')  # Your Azure AD application client ID
authority = f"https://login.microsoftonline.com/{os.getenv('AZURE_TENANT_ID')}"  # Your Azure AD tenant ID



def main():
	"""run streamlit app"""
	load_dotenv()
	# Initialize Msal
	auth_data = Msal.initialize(
		client_id=client_id,
		authority=authority,
		scopes=[]  # Add any scopes your app needs, e.g., ["User.Read"]
	)

	cols = st.columns(2)  # Create 2 columns for buttons
	with cols[0]:
		if st.button("Sign out"):
			Msal.sign_out()  # Clears auth_data
	with cols[1]:
		if st.button("Sign in"):
			Msal.sign_in()  # Show popup to select account

	# Check if the user is authenticated
	if auth_data:
		st.write("You are signed in!")
		account = auth_data["account"]
		name = account["name"]
		st.write(f"Welcome {name}!")

		st.header("Azure Policy Exemption Tool", divider='rainbow')
		# Initialize subscription_id
		subscription_id = None
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
	else:
		st.write("Authenticate to access Azure Policy Exemption Tool")
		st.stop()


if __name__ == "__main__":
	main()
