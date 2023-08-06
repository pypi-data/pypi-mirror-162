# Empiric Network

## About

For more information, see the project's repository [here](https://github.com/42labs/Empiric).

## Usage

### Publishing a Price Feed

First, please register with the Empiric team. Currently being a data publisher is permissioned, while we build out the safeguards that will allow us to enable anyone to be a data publisher in the future. Reach out to @EmpiricNetwork on Telegram to inquire about becoming a data publisher.

Once you have chosen your publisher_id and have a public/private key pair that is registered, you can start publishing prices!

Simply install this package and run:

```
from empiric.core.entry import construct_entry
from empiric.publisher.client import EmpiricPublisherClient

client = EmpiricPublisherClient(private_key, publisher_address)
entry = construct_entry(key, value, timestamp, publisher)
client.publish(entry)
```