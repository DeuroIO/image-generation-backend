import boto3
import os
import json
from gan_io import process_a_image_using_gan
from shutil import copyfile

converted_directory = "s3_files"
if not os.path.exists(converted_directory): os.makedirs(converted_directory)

out_bucket = boto3.resource('s3').Bucket('deuro-image-uploads')
finished_bucket = 'deuro-image-finished-processing'

sqs = boto3.client('sqs')
#QUEUE URL
queue_url = "https://sqs.us-east-2.amazonaws.com/232968121261/deuro-image-queue"

def download_from_s3(s3_file):
    """
    Download a file from the S3 output bucket to your hard drive.
    """
    splits = s3_file.split(".")
    prefix = splits[0]
    destination_path = os.path.join(converted_directory, prefix)
    destination_pathA = "{}/testA".format(destination_path)
    destination_pathB = "{}/testB".format(destination_path)
    try:
        os.makedirs(destination_pathA)
        os.makedirs(destination_pathB)
    except:
        print()
    body = out_bucket.Object(s3_file).get()['Body']
    with open("{}/{}".format(destination_pathA, os.path.basename(s3_file)), 'wb') as destA:
        with open("{}/{}".format(destination_pathB, os.path.basename(s3_file)), 'wb') as destB:
            # Here we write the file in chunks to prevent
            # loading everything into memory at once.
            for chunk in iter(lambda: body.read(4096), b''):
                destA.write(chunk)
                destB.write(chunk)

    print("Downloaded {0}".format(destination_path))
    return prefix

def upload_to_s3(prefix, processed_images):
    #Copy the processed data over
    target_path = "{}/{}".format(converted_directory, prefix)
    for model in processed_images:
        img = processed_images[model]
        suffix = "jpg"
        img_path = "{}.{}".format(img, suffix)
        if not os.path.isfile(img_path): suffix = "png"
        img_path = "{}.{}".format(img, suffix)
        img_file = "{}/{}_{}.{}".format(target_path, prefix, model, suffix)
        copyfile(img_path, img_file)

    # Upload the whole folder
    os.system("aws s3 sync {} s3://{}".format(target_path, finished_bucket))
    print("Uploaded {}".format(target_path))

def check_message():
    print("Check message activate!")
    # Process messages by printing out body
    response = sqs.receive_message(QueueUrl=queue_url)
    if 'Messages' not in response: return

    messages = response['Messages']
    receipt_handles = []

    for index, msg in enumerate(messages):
        receipt_handles.append({'Id': str(index), 'ReceiptHandle': msg['ReceiptHandle']})

        # Print out the body of the message
        sub_message = json.loads(json.loads(msg['Body'])['Message'])
        first_record = sub_message['Records'][0]
        key = first_record['s3']['object']['key']

        #Download file from S3
        prefix = download_from_s3(key)

        #TODO: Process the file
        processed_images = process_a_image_using_gan(prefix)

        #TODO: Upload the finished file to S3
        upload_to_s3(prefix, processed_images)

    # Let the queue know that the message is processed
    sqs.delete_message_batch(QueueUrl=queue_url, Entries=receipt_handles)
    print('Received and deleted message: %s' % messages)
