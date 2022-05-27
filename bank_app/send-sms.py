# Download the helper library from https://www.twilio.com/docs/python/install
import os
from twilio.rest import Client


# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = 'ACb82a519e91ea148938a5f8f69bd1d989'
auth_token = 'cc4f9cbd6758a73fb66c89a195b9dfa9'
client = Client(account_sid, auth_token)

message = client.messages \
                .create(
                     body="You got money",
                     from_='+14782092875',
                     to='+4550253350'
                 )

print(message.sid)