pipeline {
    agent any

    environment {
        VENV = "venv"
        METRICS_FILE = "app/artifacts/metrics.json"
        DOCKER_IMAGE = "your_dockerhub_username/your_image_name"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

      
        stage('Setup Python Virtual Environment') {
            steps {
                sh '''
                    python3 -m venv $VENV
                    . $VENV/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

      
        stage('Train Model') {
            steps {
                sh '''
                    . $VENV/bin/activate
                    mkdir -p app/artifacts
                    python train.py
                '''
            }
        }

      
        stage('Read Accuracy') {
            steps {
                script {
                    def metrics = readJSON file: "${METRICS_FILE}"
                    env.CURRENT_ACCURACY = metrics.accuracy.toString()
                    echo "Current Accuracy: ${env.CURRENT_ACCURACY}"
                }
            }
        }

        
        stage('Compare Accuracy') {
            steps {
                script {
                    withCredentials([string(credentialsId: 'best-accuracy', variable: 'BEST_ACC')]) {
                        echo "Best Stored Accuracy: ${BEST_ACC}"

                        if (env.CURRENT_ACCURACY.toFloat() > BEST_ACC.toFloat()) {
                            env.MODEL_IMPROVED = "true"
                            echo "Model improved!"
                        } else {
                            env.MODEL_IMPROVED = "false"
                            echo "Model did NOT improve."
                        }
                    }
                }
            }
        }

        
        stage('Build Docker Image') {
            when {
                expression { env.MODEL_IMPROVED == "true" }
            }
            steps {
                script {
                    docker.build("${DOCKER_IMAGE}:${env.BUILD_NUMBER}")
                }
            }
        }

       
        stage('Push Docker Image') {
            when {
                expression { env.MODEL_IMPROVED == "true" }
            }
            steps {
                script {
                    withCredentials([usernamePassword(
                        credentialsId: 'dockerhub-creds',
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASS'
                    )]) {

                        sh '''
                            echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin
                            docker tag ${DOCKER_IMAGE}:${BUILD_NUMBER} ${DOCKER_IMAGE}:latest
                            docker push ${DOCKER_IMAGE}:${BUILD_NUMBER}
                            docker push ${DOCKER_IMAGE}:latest
                        '''
                    }
                }
            }
        }
    }

 -
    post {
        always {
            archiveArtifacts artifacts: 'app/artifacts/**', fingerprint: true
        }
    }
}
