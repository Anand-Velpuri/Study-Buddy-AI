pipeline {
    agent any
    environment {
        DOCKER_HUB_REPO = "anandvelpuri/studybuddyai"
        DOCKER_HUB_CREDENTIALS_ID = "dockerhub-token"
        IMAGE_TAG = "v${BUILD_NUMBER}"
    }
    stages {
        // 1. This stage ALWAYS runs so Jenkins can evaluate the git history
        stage('Checkout Github') {
            steps {
                echo 'Checking out code from GitHub...'
                checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'github-token', url: 'https://github.com/Anand-Velpuri/Study-Buddy-AI.git']])
            }
        }        

        // 2. PARENT STAGE: This whole block skips if only k8s/ files were changed
        stage('Application CI/CD') {
            when {
                not {
                    changeset "k8s/**"
                }
            }
            // All your actual build steps are nested inside here
            stages {
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
                                git config user.name "jenkins-bot"
                                git config user.email "jenkins@studybuddy.ai"
                                git add k8s/deployment.yaml
                                git commit -m "Update image tag to ${IMAGE_TAG}" || echo "No changes to commit"
                                git push https://${GIT_USER}:${GIT_PASS}@github.com/Anand-Velpuri/Study-Buddy-AI.git HEAD:main
                                '''
                            }
                        }
                    }
                }
                stage('Install Kubectl & ArgoCD CLI Setup') {
                    steps {
                        sh '''
                        echo 'installing Kubectl & ArgoCD cli...'
                        curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
                        chmod +x kubectl
                        mv kubectl /usr/local/bin/kubectl
                        curl -sSL -o /usr/local/bin/argocd https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
                        chmod +x /usr/local/bin/argocd
                        '''
                    }
                }
                stage('Apply Kubernetes & Sync App with ArgoCD') {
                    steps {
                        script {
                            kubeconfig(credentialsId: 'kubeconfig', serverUrl: 'https://192.168.49.2:8443') {
                                sh '''
                                argocd login ec2-13-233-51-196.ap-south-1.compute.amazonaws.com:31704 --username admin --password $(kubectl get secret -n argocd argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d) --insecure
                                argocd app sync study
                                '''
                            }
                        }
                    }
                }
            } // End of nested stages
        } // End of Parent Stage
    }
}