import json
import boto3
import secrets
import time


def provision_ct_account(doc):
    sts = boto3.client('sts')
    servicecatalog = boto3.client('servicecatalog')
    s3 = boto3.resource('s3')
    response1 = sts.get_caller_identity()
    AdminArn = "arn:aws:iam::" + response1['Account'] + ":role/service-role/AWSControlTowerStackSetRole"
    REGION = "us-east-1"
    response2 = servicecatalog.search_products(Filters={'FullTextSearch': ["AWS Control Tower Account Factory"]})
    prod_id = response2['ProductViewSummaries'][0]['ProductId']
    response3 = servicecatalog.describe_product(Id=prod_id)
    pa_id = response3['ProvisioningArtifacts'][0]['Id']
    RandomToken = secrets.token_hex(5)
    CatalogName = "CatalogFor" + doc[4]['Value']
    ProvisionAccount = servicecatalog.provision_product(ProductId=prod_id, ProvisioningArtifactId=pa_id,
                                                        ProvisionToken=RandomToken, ProvisioningParameters=doc,
                                                        ProvisionedProductName=CatalogName)
    print(ProvisionAccount)
    response4 = servicecatalog.scan_provisioned_products()
    STATUS = response4['ProvisionedProducts'][0]['Status']
    print(STATUS)
    while STATUS != "AVAILABLE":
        print(STATUS)
        time.sleep(30)
        response4 = servicecatalog.scan_provisioned_products()
        STATUS = response4['ProvisionedProducts'][0]['Status']

    return {'statusCode': 200}

if __name__ == "__main__":
    doc = json.loads(open('params.json', 'rb').read())
    provision_ct_account(doc)