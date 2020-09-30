import deployment_scripts.make_artifact_bucket as bk
import deployment_scripts.create_cmf_stack as cmf
import deployment_scripts.create_secure_ssm as ssm
import deployment_scripts.create_cognito_user as user
import deployment_scripts.cloudendure_helper as helper
import subprocess, sys, json
from src.framework.python import setup_cloudendure_project
import deployment_scripts.create_vpc as vpc
import deployment_scripts.create_security_group as sg
import deployment_scripts.create_security_group_ingress as sg_ingress

if __name__ == "__main__":

    # Reading environment variables file
    with open("src/framework/config/config.json") as parameter_fileobj:
        parameter_data = json.load(parameter_fileobj)
        project = parameter_data['PROJECT']
        environment = parameter_data['ENV']
        mr_profile = parameter_data['AWS_MIGRATION_PROFILE']
        dr_profile = parameter_data['AWS_DR_PROFILE']

    mr_vpc_parameters = {}
    dr_vpc_parameters = {}
    # Reading vpc config file
    with open("src/framework/config/vpc.json") as vpc_config:
         vpc_parameters = json.load(vpc_config)

    # Creation of Migration VPC
    mr_vpc_parameters['Project'] = project
    mr_vpc_parameters['Environment'] = environment
    mr_vpc_parameters['VpcName'] = vpc_parameters['VPC_MR_NAME']
    mr_vpc_parameters['VpcCidrBlock'] = vpc_parameters['VPC_MR_CIDR']
    mr_vpc_parameters['PublicSubnets'] = vpc_parameters['PublicSubnetsMR']
    mr_vpc_parameters['PrivateSubnets'] = vpc_parameters['PrivateSubnetsMR']
    vpc.create_stack(mr_vpc_parameters,mr_profile)

    # Creation of DR VPC
    dr_vpc_parameters['Project'] = project
    dr_vpc_parameters['Environment'] = environment
    dr_vpc_parameters['VpcName'] = vpc_parameters['VPC_DR_NAME']
    dr_vpc_parameters['VpcCidrBlock'] = vpc_parameters['VPC_DR_CIDR']
    dr_vpc_parameters['PublicSubnets'] = vpc_parameters['PublicSubnetsDR']
    dr_vpc_parameters['PrivateSubnets'] = vpc_parameters['PrivateSubnetsDR']
    vpc.create_stack(dr_vpc_parameters,dr_profile)

    # Reading security group config file
    with open("src/framework/config/sg.json") as sg_config:
        sg_data = json.load(sg_config)

    #Creating Security Groups
    for sg_obj in sg_data['SecurityGroups']:
        sg_params = sg_obj
        sg_params['Project'] = project
        sg_params['Environment'] = environment
        sg.create_stack(sg_params,sg_obj['profile'])
        sg_ingress.create_stack(sg_params,sg_obj['profile'])

    # Creating artifacts S3 Bucket
    bk.create_bucket(project,environment)

    # Packaging CMAF main CF template
    p = subprocess.Popen(["powershell.exe",
                          ".\\deployment_scripts\\package-template.ps1",
                          project, environment,parameter_data['AWS_MIGRATION_PROFILE']],
                         stdout=sys.stdout)
    p.communicate()

    # Creating Secure SSM parameter for linux user
    ssm.create_ssm(project,environment,'linux','password','Test@123!')
    # Creating Secure SSM parameter for windows user
    ssm.create_ssm(project,environment,'windows','password','Test@123!')

     # CMAF main stack parameters
    cmaf_parameters = {}
    cmaf_parameters['Project'] = project
    cmaf_parameters['Environment'] = environment
    cmaf_parameters['CognitoUserEmail'] = parameter_data['COGNITO_USER_EMAIL']
    cmaf_parameters['CloudEndureUsername'] = parameter_data['CE_EMAIL']
    cmaf_parameters['CloudEndureURL'] = parameter_data['CE_URL']
    cmaf_parameters['VpcName'] = vpc_parameters['VPC_MR_NAME']

     # Creating main CMAF CF stack
    cmf.create_stack(cmaf_parameters, 'cloudformation/packaged-cmaf-main-script.yaml')

    #Creating SSM Keys and Cognito user creation in Userpool
    email_key = '/' + project + '/' + environment + '/factory/username'
    userpool_key = '/' + project + '/' + environment + '/cognito/userpool_id'
    appclient_key = '/' + project + '/' + environment + '/cognito/app_client_id'
    user.create(email_key, userpool_key, appclient_key)

    #Generating Cloud Endure Api Token
    helper.generate_api_token(project,environment)

    #Create and Setup CloudEndure project
    setup_cloudendure_project.main()

