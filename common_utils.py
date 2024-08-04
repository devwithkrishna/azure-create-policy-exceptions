import pytz
import argparse
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta  # To handle months


def calculate_expiry(expires_after: int, unit: str) -> str:
    now = datetime.now(pytz.utc)  # Get the current time in UTC

    if unit == 'day':
        expiry_date = now + timedelta(days=expires_after)
    elif unit == 'month':
        expiry_date = now + relativedelta(months=expires_after)
    elif unit == 'hour':
        expiry_date = now + timedelta(hours=float(expires_after))
    else:
        raise ValueError("Invalid unit. Use 'hour', 'day', or 'month'.")

    return expiry_date.strftime('%Y-%m-%dT%H:%M:%SZ')

def main():
	"""

	:return:
	"""
	# return_date_time()
	parser = argparse.ArgumentParser(description="Calculate expiry date based on input duration.")
	parser.add_argument("--expires_after", type=int, required=True, help="Number of units for expiry.")
	parser.add_argument("--unit", type=str, choices=['hour', 'day', 'month'], default='day',
						help="Unit of time for expiry.")
	args = parser.parse_args()

	try:
		expiry_date = calculate_expiry(args.expires_after, args.unit)
		print(f"Expiry date: {expiry_date}")
	except ValueError as e:
		print(f"Error: {e}")


if  __name__ == "__main__":
	main()