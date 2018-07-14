import boto3
import os
import json
converted_directory = "s3_files"
if not os.path.exists(converted_directory):
    os.makedirs(converted_directory)

out_bucket = boto3.resource('s3').Bucket('deuro-image-uploads')
finished_bucket = boto3.resource('s3').Bucket('deuro-image-finished-processing')
# Get the service resource
sqs = boto3.client('sqs')

# Get the queue
queue = boto3.resource('sqs').get_queue_by_name(QueueName='deuro-image-queue', QueueOwnerAWSAccountId='232968121261')

#QUEUE URL
queue_url = "https://sqs.us-east-2.amazonaws.com/232968121261/deuro-image-queue"

def download_from_s3(s3_file):
    """
    Download a file from the S3 output bucket to your hard drive.
    """
    destination_path = os.path.join(
        converted_directory,
        os.path.basename(s3_file)
    )
    body = out_bucket.Object(s3_file).get()['Body']
    with open(destination_path, 'wb') as dest:
        # Here we write the file in chunks to prevent
        # loading everything into memory at once.
        for chunk in iter(lambda: body.read(4096), b''):
            dest.write(chunk)

    print("Downloaded {0}".format(destination_path))

def upload_to_s3(file):
    # Upload a new file
    data = open(os.path.join(converted_directory,file), 'rb')
    finished_bucket.put_object(Key=file, Body=data)
    print("Uploaded {}".format(file))

def check_message():
    print("Check message activate!")
    # Process messages by printing out body
    for message in queue.receive_messages():
        # Print out the body of the message
        body = json.loads(message.body)
        sub_message = json.loads(body['Message'])
        print(body)
        outputs = sub_message['Records']
        if not len(outputs):
            print("Saw no output in {0}".format(body))

        key = outputs[0].get('s3').get('object').get('key')

        if not key:
            print("Saw no key in outputs in {0}".format(body))

        #Download file from S3
        download_from_s3(key)

        #TODO: Process the file


        #TODO: Upload the finished file to S3

        # Let the queue know that the message is processed
        sqs.delete_message(QueueUrl=queue_url, Entries=sub_message['ReceiptHandle'])
