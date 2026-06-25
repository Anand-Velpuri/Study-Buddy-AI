pipeline {
    agent any
    environment {
        DOCKER_HUB_REPO = "anandvelpuri/studybuddyai"
        DOCKER_HUB_CREDENTIALS_ID = "dockerhub-token"
        IMAGE_TAG = "v${BUILD_NUMBER}"
    }
    stages {
        stage('Checkout Github') {
            steps {
                echo 'Checking out code from GitHub...'
                checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'github-token', url: 'https://github.com/Anand-Velpuri/Study-Buddy-AI.git']])
            }
        }        
        stage('Build Docker Image') {
            steps {
                script {
                    echo 'Building Docker image...'
                    dockerImage = docker.build("${DOCKER_HUB_REPO}:${IMAGE_TAG}")
                }
            }
        }
        stage('Push Image to DockerHub') {
            steps {
                script {
                    echo 'Pushing Docker image to DockerHub...'
                    docker.withRegistry('https://registry.hub.docker.com' , "${DOCKER_HUB_CREDENTIALS_ID}") {
                        dockerImage.push("${IMAGE_TAG}")
                    }
                }
            }
        }
        stage('Update Deployment YAML with New Tag') {
            steps {
                script {
                    sh """
                    sed -i 's|image: anandvelpuri/studybuddyai:.*|image: anandvelpuri/studybuddyai:${IMAGE_TAG}|' k8s/deployment.yaml
                    """
                }
            }
        }

        stage('Commit Updated YAML') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'github-token', usernameVariable: 'GIT_USER', passwordVariable: 'GIT_PASS')]) {
                        sh '''
                        git config user.name "Anand-Velpuri"
                        git config user.email "velpurianand8005@gmail.com"
                        git add k8s/deployment.yaml
                        git commit -m "Update image tag to ${IMAGE_TAG}" || echo "No changes to commit"
                        git push https://${GIT_USER}:${GIT_PASS}@github.com/Anand-Velpuri/Study-Buddy-AI.git HEAD:main
                        '''
                    }
                }
            }
        }
        
    }
}