pipeline {
    agent any

    environment {
        VENV = "venv"
        METRICS_FILE = "app/artifacts/metrics.json"
        DOCKER_IMAGE = "mdjaasir2022bcs0010/wine_predict_2022bcs0010"
        MODEL_IMPROVED = "false"
    }

    stages {

        // -----------------------------
        // Stage 1: Checkout
        // -----------------------------
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        // -----------------------------
        // Stage 2: Setup Python Virtual Environment
        // -----------------------------
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

        // -----------------------------
        // Stage 3: Train Model
        // -----------------------------
        stage('Train Model') {
            steps {
                sh '''
                    . $VENV/bin/activate
                    mkdir -p app/artifacts
                    python train.py
                '''
            }
        }

        // -----------------------------
        // Stage 4: Read Metrics (MSE & R2)
        // -----------------------------
        stage('Read Metrics') {
            steps {
                script {
                    def metrics = readJSON file: "${METRICS_FILE}"

                    env.CURRENT_MSE = metrics.mse.toString()
                    env.CURRENT_R2  = metrics.r2.toString()

                    echo "Current MSE: ${env.CURRENT_MSE}"
                    echo "Current R2: ${env.CURRENT_R2}"
                }
            }
        }

        // -----------------------------
        // Stage 5: Compare Model Performance
        // -----------------------------
        stage('Compare Model Performance') {
            steps {
                script {
                    withCredentials([string(credentialsId: 'best-accuracy', variable: 'BASELINE')]) {

                        def parts = BASELINE.split(',')

                        def BEST_MSE = parts[0].toFloat()
                        def BEST_R2  = parts[1].toFloat()

                        echo "Best Stored MSE: ${BEST_MSE}"
                        echo "Best Stored R2: ${BEST_R2}"

                        // Model improves if:
                        // R2 increases AND MSE decreases

                        if (env.CURRENT_R2.toFloat() > BEST_R2 &&
                            env.CURRENT_MSE.toFloat() < BEST_MSE) {

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

        // -----------------------------
        // Stage 6: Build Docker Image (Conditional)
        // -----------------------------
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

        // -----------------------------
        // Stage 7: Push Docker Image (Conditional)
        // -----------------------------
        stage('Push Docker Image') {
            when {
                expression { env.MODEL_IMPROVED == "true" }
            }
            steps {
                script {
                    withCredentials([usernamePassword(
                        credentialsId: 'docker-access',
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

    // -----------------------------
    // Always archive artifacts
    // -----------------------------
    post {
        always {
            archiveArtifacts artifacts: 'app/artifacts/**', fingerprint: true
        }
    }
}
