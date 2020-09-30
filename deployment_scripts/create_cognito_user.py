import boto3
import json
from botocore.exceptions import ClientError

with open('src\\framework\\config\\config.json', 'rb') as f:
    configs = json.load(f)
session = boto3.Session(profile_name=configs['AWS_MIGRATION_PROFILE'])

#Creating a boto3 client object for cognito
client = session.client(service_name='cognito-idp')

#Creating a boto3 ssm object for ssm
ssm = session.client(service_name='ssm')

#Creating a boto3 secrets manager for secrets manager
secrets = session.client(service_name='secretsmanager')

#Creating a boto3 client object for ses
client = session.client(service_name='ses')

#Group Type
type = 'admin'


def authenticate_user(client_id, user_name, password, new_password):
    try:
        response = client.initiate_auth(
            ClientId=client_id,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': user_name,
                'PASSWORD': password
            }
        )
        session_id = response['Session']
        if session_id != '':
            response = client.respond_to_auth_challenge(
                ClientId=client_id,
                ChallengeName='NEW_PASSWORD_REQUIRED',
                Session=session_id,
                ChallengeResponses={
                    'NEW_PASSWORD': new_password,
                    'USERNAME': user_name}
            )
            access_token = response['AuthenticationResult']['AccessToken']
            return access_token
        else:
            print("The session is empty couldn't proceed")
    except ClientError as error:
        raise error


def get_random_password(length):
    try:
        if length >= 6:
            response = secrets.get_random_password(
                PasswordLength=length,
                ExcludeNumbers=False,
                ExcludePunctuation=False,
                ExcludeUppercase=False,
                ExcludeLowercase=False,
                RequireEachIncludedType=True
            )
            return response['RandomPassword']
        else:
            print("Length < 6 | Can not create a user")
    except ClientError as error:
        raise error


def put_ssm_parameters(name, description, value):
    try:
        response = ssm.put_parameter(
            Name=name,
            Description=description,
            Value=value,
            Type='SecureString',
            Overwrite=True,
            Tier='Standard'
        )
        return response['Version']
    except ClientError as error:
        raise error


def get_ssm_parameters(name):
    try:
        response = ssm.get_parameter(
            Name=name,
            WithDecryption=True
        )
        return response['Parameter']['Value']
    except ClientError as error:
        if error.response['Error']['Code'] == 'ParameterNotFound':
            return 'NULL'
        else:
            raise error


def user_creation(user_pool_id, email, password):
    try:
        response = client.admin_create_user(
            UserPoolId=user_pool_id,
            Username=email,
            UserAttributes=[
                {
                    'Name': 'email',
                    'Value': email
                }
            ],
            TemporaryPassword=password,
            ForceAliasCreation=False,
            DesiredDeliveryMediums=[
                'EMAIL'
            ]
        )
        return response
    except ClientError as error:
        print("Exception message: {}".format(error))


def add_user_group(user_pool_id, email, type):
    try:
        response = client.admin_add_user_to_group(
            UserPoolId=user_pool_id,
            Username=email,
            GroupName=type
        )
        return response
    except ClientError as error:
        raise error


def send_email(recipient_email, new_password, url, sender_email):
    try:
        #Adding Details for the email
        subject = "Congratulations you are confirmed"
        body_text = ("Your email is: " + recipient_email +
                     "and your password is: " + new_password +
                     "Please Click the link to sign in: " + url
                     )

        # Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    recipient_email,
                ],
            },
            Message={
                'Body': {
                    'Text': {
                        'Data': body_text
                    }
                },
                'Subject': {
                    'Data': subject,
                },
            },
            Source=sender_email,
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        return "Confirmation Email Sent Successfully! " \
               "Message ID is: " + response['MessageId']



def create(email_key,userpool_key,clientapp_key):

    # Reading environment variables file
    with open("src/framework/config/config.json") as parameter_fileobj:
        parameter_data = json.load(parameter_fileobj)
        project = parameter_data['PROJECT']
        environment = parameter_data['ENV']

    #For getting the parameters in SSM Format
    sender_key = '/' + project + '/' + environment + '/ses/sender_email'
    cloudfront_key = '/' + project + '/' + environment + '/cloudfront/migration_factory_url'

    # For Storing the permanent password in parameter store
    name = '/' + project + '/' + environment + '/factory/password'

    #Getting SSM Parameters
    email = get_ssm_parameters(email_key)
    user_pool_id = get_ssm_parameters(userpool_key)
    client_id = get_ssm_parameters(clientapp_key)
    cloudfront_url = get_ssm_parameters(cloudfront_key)
    sender_email = get_ssm_parameters(sender_key)

    #Getting the temporary password
    password = get_random_password(10)

    #Getting the permanent password
    new_password = get_random_password(10)

    # count = 1
    # while get_ssm_parameters(name + str(count)) != 'NULL':
    #     count = count + 1
    # #name = '/' + project + '/' + environment + '/factory/'+str(count)+'/password'

    description = "This is the password"
    if email and password and user_pool_id and client_id:
        user_object = user_creation(user_pool_id, email, password)
        if user_object:
            print("Congratulations the user is created successfully")
            group_object = add_user_group(user_pool_id, email, 'admin')
            if group_object:
                print("Congratulations the user is added into the user group successfully")
                authentication_object = authenticate_user(client_id, email, password, new_password)
                if authentication_object:
                    print("Congratulations the user is authenticated successfully")
                    ssm_object = put_ssm_parameters(name, description, new_password)
                    if ssm_object:
                        print("Congratulations the "+name+" parameter is stored in ssm successfully")
                        response = send_email(email, new_password, cloudfront_url, sender_email)
                        print(response)
                    else:
                        print("SSM Object is Empty | Unable to save ssm parameter")
                else:
                    print("Authenticate Object is Empty | Unable to authenticate a user")
            else:
                print("Group Object is Empty | Unable to add user to the group")
        else:
            print("User Object is empty | Unable to create a user")
    else:
        print("Error in getting the ssm parameters")