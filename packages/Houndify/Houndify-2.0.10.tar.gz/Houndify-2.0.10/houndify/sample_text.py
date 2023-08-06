#!/usr/bin/env python3
import houndify
import argparse
import json


def send_text_query(text_query, client_id, client_key):
  requestInfo = {
    ## Pretend we're at SoundHound HQ.  Set other fields as appropriate
    'Latitude': 37.388309, 
    'Longitude': -121.973968
  }

  client = houndify.TextHoundClient(client_id, client_key, "test_user", requestInfo)

  response = client.query(text_query)
  return response

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('QUERY', type=str,
                      help='The text query that will be sent to the Hybrid Engine')
  parser.add_argument('--client-id', '-id', required=True,
                      help="Houndify client ID")
  parser.add_argument('--client-key', '-key', required=True,
                      help="Houndify client Key")

  args = parser.parse_args()

  response = send_text_query(args.QUERY, args.client_id, args.client_key)

  print(json.dumps(response, indent=2, sort_keys=True, ensure_ascii=False))

