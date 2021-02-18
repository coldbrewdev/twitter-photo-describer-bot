from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
import traceback
import tweepy
import requests
import urllib.parse
import datetime as dt
import os
import random
import config


def publish_to_describer(image_string):
    """Takes an image file name and publishes it to twitter with ComputerVision description"""
    # Generate the Image URL and local location
    remote_image_url = config.online_image_folder + image_string
    image_location = config.local_image_folder + image_string
    # Authenticate with Twitter
    auth = tweepy.OAuthHandler(config.consumer_key, config.consumer_secret)
    auth.set_access_token(config.access_token, config.access_token_secret)
    api = tweepy.API(auth)
    api.verify_credentials()
    print("Twitter Authentication OK")
    # Connect to ComputerVision
    subscription_key = config.subscription_key
    endpoint = config.endpoint
    computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))
    description_results = computervision_client.describe_image(remote_image_url)
    # Get the captions (descriptions) from the response, with confidence level
    tweet = ''
    print("Description of remote image: ")
    if len(description_results.captions) == 0:
        print("No description detected.")
    else:
        for caption in description_results.captions:
            print("'{}' with confidence {:.2f}%".format(caption.text, caption.confidence * 100))
            tweet = caption.text
    # Upload image
    media = api.media_upload(image_location)
    # Post tweet with image
    api.update_status(status=tweet, media_ids=[media.media_id])


def send_message(bot, chat, message):
    parse = urllib.parse.quote_plus(message)
    response = requests.get("https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}".format(bot, chat, parse))
    return response


def files_by_format(path, formats):
    files = os.listdir(path)
    file_list = [f for f in files if f.endswith(formats)]
    return file_list


def update_error_log(message):
    with open("error_log.txt", "a") as f:
        f.write(str(dt.datetime.now()))
        f.write('\n')
        f.write(message + "\n")
    f.close()


def main():
    """Selects a random jpeg file, publishes it, logs it, deletes it"""
    image_files = files_by_format(config.local_image_folder, ('.jpeg', '.png', '.jpg'))
    if len(image_files) in [1, 2, 5, 10]:
        message = 'There are ' + str(len(image_files)) + ' photos left in Describer (including today\'s photo).'
        send_message(config.bot_id, config.chat_id, message)
    if not image_files:
        send_message(config.bot_id, config.chat_id, 'Describer is out of photos.')
        raise SystemExit
    file = random.choice(image_files)
    t = str(dt.datetime.now())
    publish_to_describer(file)
    with open(config.local_image_folder + 'log_sent_photos.txt', 'a') as log:
        log.write(file + ' ' + t + '\n')
    os.remove(config.local_image_folder + file)


if __name__ == '__main__':
    current_hour = dt.datetime.utcnow().hour
    try:
        if current_hour in [1, 17]:  # Allows change of post frequency without updating cron (w/ cron calling hourly)
            main()
    except Exception as e:
        x = str(e)
        y = ''.join(traceback.format_exc())
        send_message(config.bot_id, config.chat_id, 'Describer encountered an error.')
        update_error_log('Describer' + x+y)
