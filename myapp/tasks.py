from twilio.rest import Client
from django.conf import settings

def place_missed_call(phone_number):
    account_sid = 'AC07e99ac1f2920beb8fd9e26b1fc8ceb7'
    auth_token = '3d7b1010f7708df91108431a7f40b9cb'
    from_number = '+17432006239'

    client = Client(account_sid, auth_token)

    try:
        call = client.calls.create(
            to=phone_number,
            from_=from_number,
            url='http://demo.twilio.com/docs/voice.xml'
        )
        return f"Call placed: {call.sid}"
    except Exception as e:
        return f"Call failed: {str(e)}"

# Optional hook to log success/failure
def log_result(task):
    print(f"🔔 Task '{task.name}' finished with result: {task.result}")
