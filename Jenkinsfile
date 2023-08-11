pipeline {
   agent any

   environment {
       AWS_DEFAULT_REGION = 'ap-south-1'
       AWS_ACCESS_KEY_ID = credentials('AccessKeyID')
       AWS_SECRET_ACCESS_KEY = credentials('SecretAccessKey')
   }

   stages {
       stage('Gathering Framework Manifest Files') {
           steps {
               checkout scm
           }
       }

    stage('Ready for Cost Optimization ?') {
      input {
        message "Are you ready for Miracle to Happen ?"
        ok "Go Ahead!"
      }
      steps {
        echo 'Accepted'
      }
    }

    stage('Gathering Pre-Processors') {
      steps {
        sh "sleep 5"
      }
    }

       stage('Cost Optimization Framework Deployment in Progress') {
           steps {
               script {
                   sh """
                       aws cloudformation deploy \\
                           --region \$AWS_DEFAULT_REGION \\
                           --template-file CloudFormation/costOptimization.yml \\
                           --stack-name CostOptimizationStack \\
                           --parameter-overrides MemorySize=1024 Timeout=900 \\
                           --capabilities CAPABILITY_IAM
                   """
               }
           }
       }
    stage('Calculating Cost($) Savings!!') {
      steps {
        echo "Cost Optimization lever deployed! Still, we are fetching tentative savings for you!"
        sh "sleep 180"
      }
    }
    stage('Done!! Do you want to Cleanup ?') {
      input {
        message "Are you sure?"
        ok "Go Ahead!"
      }
      steps {
        echo 'Accepted'
      }
    }
       stage('Cleanup in Progress') {
           steps {
               script {
                   sh """
                       aws cloudformation delete-stack \\
                           --region \$AWS_DEFAULT_REGION \\
                           --stack-name CostOptimizationStack
                   """
               }
           }
       }
   }
}
