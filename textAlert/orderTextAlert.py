import requests
import time
from datetime import datetime
from config import Config
from daemon import Daemon
import sys
from getopt import getopt, GetoptError
import logging
from systemd import journal

pending_array = []

init_dt = datetime.now()

l = logging.getLogger(__name__)
logging.basicConfig(filename="out.log", level=logging.INFO)


# add the journal handler to the current logger
l.addHandler(journal.JournalHandler())

l.info("Starting notifier service at " + str(datetime.utcnow()))

def orderAlertCoro(sleep_period: int = 60): 	
	l.info("Coroutine start")
	while 1:
		r = requests.get(
			f"https://commerce.goodbarber.dev/publicapi/v1/general/orders/{Config.WEBZINE_ID}?status=delivered",
			headers={"token": Config.GB_TOKEN},
		).json()

		if not "error_code" in r:

			for i in r["orders"]:
				# Has the order already been handled and is it a new one?
				if (
					i["order_num"] not in pending_array
					and datetime.fromisoformat(i["created_at"][:-1]) >= init_dt
				):
					l.info(f"-- NEW ORDER: n°{i['order_num']} FETCHED --------")

					r = requests.post(
						f"https://api.twilio.com/2010-04-01/Accounts/{Config.TWILIO_SID}/Messages.json",
						data={
							"Body": f"""Commande n°{i['order_num']} : {i['shipping_address']['last_name']+' '+i['shipping_address']['first_name'] if i['shipping_address']!={} else 'Sans nom'}"""
							f"""{'Sur place' if i['shipping_type']=='pickup' else 'Livraison à '+i['shipping_address']['city']}"""
							f"""{len(i['items'])} articles, total: {'{:.2f}'.format(float(i['total']))}€\n"""
							f"""https://{Config.SHOP_DOMAIN}/manage/commerce/orders/{i['id']}/edit""",

							# Phone number assigned to the Twilio account
							"From": Config.FROM_PHONE_NUMBER,

							# Phone number of the recipient
							"To": Config.TO_PHONE_NUMBER,
						},
						auth=requests.auth.HTTPBasicAuth(
							Config.TWILIO_SID, Config.TWILIO_TOKEN),
					).json()

					# Add the current order's id to the array so we don't send duplicated texts
					pending_array.append(i["order_num"])

					if "code" in r or ("error_code" in r and r["error_code"] != None):
						# Error message field is named differently if the req passed pre-validation
						l.error(f"Text could not be sent: {r['message'] if not 'error_code' in r else r['error_message']}")
					else:
						l.error("Text sent!")

		else:
			l.error(
				f"Error in response: {r['error_description']} ( {r['error_code']} )")

		l.info(f"sleeping for {sleep_period}")
		time.sleep(sleep_period)

if __name__ == "__main__":
	
	is_df_daemon=[False, None] #Daemonization state, False = daemonization is handled by systemd | True = Daemonization is handled by the script itself

	try:
		opts, args = getopt(sys.argv[1:], "d:s:")
	except (GetoptError) as e:
		l.error(e)
		sys.exit(1)

	for o, a in opts:
		if o =="-d":
			if a:
				is_df_daemon=[True, a] #Set manual daemonization status and provide the action verb

			else:
				raise RuntimeError("No daemon action has been specified, (start|stop|restart)")

		elif o == "-s":
			if a:
				#TODO: Handle custom timer
				pass

			else:
				l.warn("No sleep time specified, default 60s will be used")
		
	if is_df_daemon[0]:
		d = Daemon("/tmp/textAlert.pid", orderAlertCoro)
		getattr(d, is_df_daemon[1])()

	else:
		orderAlertCoro()