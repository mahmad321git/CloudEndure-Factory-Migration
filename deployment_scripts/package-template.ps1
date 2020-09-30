param ($project,$environment,$profile)

echo 'Uploading packages to artifact S3 Bucket'

cd cloudformation

aws cloudformation package --template-file cmaf-main-script.yaml --s3-bucket $project-cf-artifact-bucket-$environment --output-template-file packaged-cmaf-main-script.yaml --profile $profile

cd ..