#!/usr/bin/env python3
import houndify
import argparse
import json
import sys
import time
import wave


class colors:
  GREEN = "\033[92m"
  RED = "\033[91m"
  ENDC = "\033[0m"


## Text Query
def send_text_query(text_query, client_id, client_key, endpoint=houndify.TEXT_ENDPOINT):
  requestInfo = {
    ## Pretend we're at SoundHound HQ.  Set other fields as appropriate
    'Latitude': 37.388309, 
    'Longitude': -121.973968
  }

  client = houndify.TextHoundClient(client_id, client_key, "test_user", requestInfo, endpoint)

  response = client.query(text_query)
  return response


## Audio Query

# Simple HoundListener; prints out partial transcript
class MyListener(houndify.HoundListener):
  def __init__(self, silence_ouput=False):
    self.print_details = not silence_ouput
  def onPartialTranscript(self, transcript):
    if self.print_details: 
      print("Partial transcript: " + transcript)
  def onFinalResponse(self, response):
    pass
  def onError(self, err):
    print(colors.RED + "Error: {}".format(err) + colors.ENDC)

def check_audio_compatibility(audio):
  if audio.getsampwidth() != 2:
    print(colors.RED + "{}: wrong sample width (must be 16-bit)".format(fname) + colors.ENDC)
    sys.exit()
  if audio.getframerate() != 8000 and audio.getframerate() != 16000:
    print(colors.RED + "{}: unsupported sampling frequency (must be either 8 or 16 khz)".format(fname) + colors.ENDC)
    sys.exit()
  if audio.getnchannels() != 1:
    print(colors.RED + "{}: must be single channel (mono)".format(fname) + colors.ENDC)
    sys.exit()


def send_audio_file(audio_file, client_id, client_key, endpoint=houndify.VOICE_ENDPOINT, silence_output=False):
  audio = wave.open(audio_file)
  check_audio_compatibility(audio)

  BUFFER_SIZE = 256
  client = houndify.StreamingHoundClient(client_id, client_key, "test_user", endpoint=endpoint)
  client.setLocation(37.388309, -121.973968)
  client.setSampleRate(audio.getframerate())
  
  client.start(MyListener(silence_output))
  
  while True:
    chunk_start = time.time()
  
    samples = audio.readframes(BUFFER_SIZE)
    chunk_duration = float(len(samples)) / (audio.getframerate() * audio.getsampwidth())
    if len(samples) == 0: break
    if client.fill(samples): break
  
    # # Uncomment the line below to simulate real-time request
    # time.sleep(chunk_duration - time.time() + chunk_start)

  audio.close()
  response = client.finish() # returns either final response or error
  return response

def check_response_transcript(response, expected_transcript):
  speech_engine_transcript = get_transcript_from_response(response)

  if expected_transcript.lower()  == speech_engine_transcript.lower():
    print(colors.GREEN + "Transcripts matched for {}".format(expected_transcript) + colors.ENDC)
    exit_code = 0
  else:
    print(colors.RED + "Transcripts did not match:" + colors.ENDC)
    print("EXPECTED_TRANSCRIPT      :{}".format(expected_transcript))
    print("SPEECH_ENGINE_TRANSCRIPT :{}".format(speech_engine_transcript))
    exit_code = 1
  
  return exit_code

def get_transcript_from_response(response):
  if 'Disambiguation' in response:
    if 'ChoiceData' in response['Disambiguation']:
      if len(response['Disambiguation']['ChoiceData'][0]) > 1:
        if 'Transcription' in response['Disambiguation']['ChoiceData'][0]:
          return response['Disambiguation']['ChoiceData'][0]['Transcription']
  print(colors.RED + "No transcript found in json response" + colors.ENDC)
  return ''

if __name__ == "__main__":
  parser = argparse.ArgumentParser()

  query_type_group = parser.add_mutually_exclusive_group(required=True)
  query_type_group.add_argument('--text-query', '-txt', type=str,
                     help='The text query that will be sent to the Hybrid Engine')
  query_type_group.add_argument('--audio-query', '-wav', type=str,
                     help='Audio .wav file to be sent to the server as an audio query')

  parser.add_argument('--client-id', '-id', required=True,
                      help="Houndify client ID")
  parser.add_argument('--client-key', '-key', required=True,
                      help="Houndify client Key")

  parser.add_argument('--endpoint', '-e',
                      help='''
                           The endpoint the SDK will hit to query Houndify.
                           text-query default: {}
                           audio-file default: {} 
                           '''.format(houndify.TEXT_ENDPOINT, houndify.VOICE_ENDPOINT))

  parser.add_argument('--expected-transcript', '-x', type=str,
                      help='''
                           The expected transcript from the audio file.
                           If this argument is provided the script will compare it to the transcript from Houndify.
                           On failure, the script will return 1
                           ''')

  parser.add_argument('--silent', '-s', dest='print_json', action='store_false',
                      help='''
                           The script will not print the server's JSON response
                           Does not silence the --expected-transcript output
                           ''')

  parser.set_defaults(print_json=True)

  args = parser.parse_args()

  # Set default endpoint to houndify backend if none was set
  if not args.endpoint:
    if args.text_query:
      args.endpoint = houndify.TEXT_ENDPOINT
    else:
      args.endpoint = houndify.VOICE_ENDPOINT

  ## text
  if args.text_query:
    response = send_text_query(args.text_query, args.client_id, args.client_key, args.endpoint)

    if args.print_json:
      print(json.dumps(response, indent=2, sort_keys=True, ensure_ascii=False))


  ## audio
  if args.audio_query:
    response = send_audio_file(args.audio_query, args.client_id, args.client_key, args.endpoint, silence_output=not args.print_json)
    
    if args.print_json:
      print(json.dumps(response, indent=2, sort_keys=True, ensure_ascii=False))

    # if the user provided an expected transcript, compare with one we got from speech engine
    if args.expected_transcript:
      sys.exit(check_response_transcript(response, args.expected_transcript))
