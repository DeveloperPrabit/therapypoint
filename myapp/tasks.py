# from celery import shared_task
# from twilio.rest import Client

# @shared_task
# def place_missed_call(phone_number):
#     account_sid = 'AC07e99ac1f2920beb8fd9e26b1fc8ceb7'
#     auth_token = 'b1b4d7f5be6bc132f9602c91a0af47bc'
#     from_number = '+9779761660142'

#     client = Client(account_sid, auth_token)

#     try:
#         call = client.calls.create(
#             to=phone_number,
#             from_=from_number,
#             url='http://demo.twilio.com/docs/voice.xml'
#         )
#         return f"Call scheduled: {call.sid}"
#     except Exception as e:
#         return f"Call failed: {str(e)}"
