import boto3
import os
import time

# Create SQS client
sqs = boto3.client('sqs')

queue_url = 'https://sqs.us-east-2.amazonaws.com/842599995920/holidaybear.fifo'
counter = 0

while True:
	# Receive message from SQS queue
	response = sqs.receive_message(
	    QueueUrl=queue_url,
	    MaxNumberOfMessages=1,
	    MessageAttributeNames=[
	        'All'
	    ],
	    VisibilityTimeout=30,
	    WaitTimeSeconds=0
	)

	try:
		print "Reading message..."
		message = response['Messages'][0]
		receipt_handle = message['ReceiptHandle']

		# Delete received message from queue
		sqs.delete_message(
		    QueueUrl=queue_url,
		    ReceiptHandle=receipt_handle
		)

		os.system("say {}".format(message['Body']))
		counter = 0

		print('Received and deleted message: %s' % message)
	except:
		counter += 1 
		if counter > 500:
			time.sleep(2)
		print "No messages. Re-reading."
		continue