pipeline {
   agent any

   environment {
       AWS_DEFAULT_REGION = 'ap-south-1'
       AWS_ACCESS_KEY_ID = credentials('AccessKeyID')
       AWS_SECRET_ACCESS_KEY = credentials('SecretAccessKey')
   }

   stages {
       stage('Checkout') {
           steps {
               checkout scm
           }
       }

       stage('Deploy CloudFormation') {
           steps {
               script {
                   def stackName = 'MyCloudFormationStack'
                   def templateFile = 'CloudFormation/costOptimization.yml'

                   sh """
                       aws cloudformation deploy \\
                           --region \$AWS_DEFAULT_REGION \\
                           --template-file \$templateFile \\
                           --stack-name \$CostOptimization \\
                   """
               }
           }
       }
   }
}
