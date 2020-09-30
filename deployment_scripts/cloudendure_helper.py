import requests
import json
import deployment_scripts.create_secure_ssm as store_ssm
import deployment_scripts.get_ssm_parameters as get_ssm


#for getting the api token
def get_api_token(url, object):
    try:
        response = requests.post(url, json=object)
        response = json.loads(response.text)
        return response['apiToken']
    except requests.exceptions.RequestException as error:
        raise error


#for generating the api token
def generate_api_token(project,environment):
    #getting cloud_endure credentials from get_ssm_parameters function
    username = get_ssm.get_ssm_parameters("/"+project+"/"+environment+"/"+"cloudendure/user_name")
    #password = get_ssm.get_ssm_parameters("/"+project+"/"+environment+"/"+"cloudendure/password")
    password = get_ssm.get_ssm_parameters("CLOUDENDURE_UI_PASSWORD")
    url = get_ssm.get_ssm_parameters("/"+project+"/"+environment+"/"+"cloudendure/url")

    #Object Credentials for the CloudEndure Account
    object = {
        "username": username,
        "password": password
    }

    #Calling the function for Api token
    response = get_api_token(url, object)

    #Setting the parameter for create_ssm parameters function
    name = "api_token"
    service = "cloudendure"
    value = response

    #Calling the put_ssm_parameters for saving the Api token
    store_ssm.create_ssm(project,environment,service,name,value)