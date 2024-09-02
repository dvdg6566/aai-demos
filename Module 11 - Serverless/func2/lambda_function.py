def lambda_handler(event, context):
	return 'Secondary Lambda function running successfully!'

if __name__ == '__main__':
	lambda_handler(None,None)