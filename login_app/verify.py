from twilio.rest import Client
account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
client = Client(account_sid, auth_token)

new_factor = client.verify \
                   .services('VAXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX') \
                   .entities('ff483d1ff591898a9942916050d2ca3f') \
                   .new_factors \
                   .create(
                        friendly_name="Taylor's Account Name",
                        factor_type='totp'
                    )

print(new_factor.binding)