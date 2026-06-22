def shellCMD(cmd) {
    return sh(script: '#!/bin/sh -e\n' + cmd, returnStdout: true).trim()
}

@groovy.transform.Field
def REPO_TAG = ''

@groovy.transform.Field
def PREV_REPO_TAG = ''

pipeline {
    agent any
    options {
        timeout(time: 20, unit: 'MINUTES')
    }
    environment {
        // --- CONFIGURATION ---
        GIT_BRANCH = 'development' // Change to your GitHub branch
        
        // Docker Hub Details
        DOCKERHUB_USERNAME = 'your-dockerhub-username' 
        IMAGE_NAME = 'your-image-name' // e.g., 'my-backend-app'
        DOCKERHUB_CREDS_ID = 'dockerhub-credentials' // Jenkins ID for DockerHub User/Pass
        
        // GitHub Credentials
        GITHUB_SSH_KEY_ID = 'jenkins-github-ssh-key' // Jenkins ID for GitHub SSH Key
        
        // Server Details
        SERVER_URL = "ssh-user@api.dhruv.in"
        SERVER_SSH_KEY_ID = 'jenkins-server-ssh-key'
        SERVER_HOME_DIR = '/home/api.dhruv.in'
    }
    stages {
        stage('Bump Version & Git Push') {
            steps {
                script {
                    // 1. Calculate Versions
                    PREV_REPO_TAG = shellCMD("bump2version --dry-run --list patch | grep current_version | cut -d '=' -f 2").replaceAll("\\r", "").trim()
                    REPO_TAG = shellCMD("bump2version --dry-run --list patch | grep new_version | cut -d '=' -f 2").replaceAll("\\r", "").trim()
                    
                    // 2. Push to GitHub
                    withCredentials([sshUserPrivateKey(credentialsId: "$GITHUB_SSH_KEY_ID", keyFileVariable: 'keyfile')]) {
                        catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                            try {
                                sh """
                                    eval `ssh-agent -s`
                                    trap "ssh-agent -k" EXIT
                                    ssh-add ${keyfile}
                                    
                                    # Config git to avoid 'who are you' errors
                                    git config user.email "jenkins@yourdomain.com"
                                    git config user.name "Jenkins CI"
                                    
                                    bump2version patch
                                    echo "Bumped from ${PREV_REPO_TAG} to ${REPO_TAG}"
                                    
                                    # Push explicitly to GitHub
                                    git push origin HEAD:${GIT_BRANCH}
                                    git push origin --tags
                                """
                            } catch (Exception e) {
                                echo "Git Push Error: ${e.getMessage()}"
                                error("Failed to push version bump to GitHub.")
                            }
                        }
                    }
                }
            }
        }
        stage('Build & Push to Docker Hub') {
            steps {
                script {
                    // This creates a tag: username/image:version
                    def fullImageName = "${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${REPO_TAG}"
                    def latestImageName = "${DOCKERHUB_USERNAME}/${IMAGE_NAME}:latest"

                    // Login to DockerHub (Registry '' implies Docker Hub default)
                    docker.withRegistry('', DOCKERHUB_CREDS_ID) {
                        try {
                            sh """
                                echo "Building Docker Image: ${fullImageName}"
                                # Build the image explicitly
                                docker build -t ${fullImageName} -t ${latestImageName} .
                                
                                # Push specific version and latest
                                docker push ${fullImageName}
                                docker push ${latestImageName}
                            """
                        } catch (Exception e) {
                            echo "Docker Error: ${e.getMessage()}"
                            error("Failed to build/push to Docker Hub.")
                        }
                    }
                }
            }
        }
        stage('Deploy to Dev Server') {
            steps {
                script {
                    withCredentials([
                        sshUserPrivateKey(credentialsId: "$SERVER_SSH_KEY_ID", keyFileVariable: 'keyfile'),
                        usernamePassword(credentialsId: "$DOCKERHUB_CREDS_ID", usernameVariable: 'D_USER', passwordVariable: 'D_PASS')
                    ]) {
                        catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                            try {
                                sh """
                                    eval `ssh-agent -s`
                                    trap "ssh-agent -k" EXIT
                                    ssh-add ${keyfile}
                                    
                                    ssh -o StrictHostKeyChecking=no ${SERVER_URL} << 'EOF'
                                    
                                    cd ${SERVER_HOME_DIR}/backend
                                    
                                    # 1. Update docker-compose.yaml tags
                                    # We replace the PREVIOUS tag with the NEW tag
                                    sed -i "s/${PREV_REPO_TAG}/${REPO_TAG}/g" docker-compose.yaml
                                    
                                    # Optional: Ensure image name points to Docker Hub, not AWS
                                    # (Only needed if you haven't manually updated the file on the server yet)
                                    # sed -i "s|.*amazonaws.com/.*:|image: ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:|g" docker-compose.yaml

                                    echo "Deploying version: ${REPO_TAG}"
                                    
                                    # 2. Login to Docker Hub on Remote Server
                                    echo "${D_PASS}" | docker login -u "${D_USER}" --password-stdin
                                    
                                    # 3. Pull and Restart
                                    docker-compose pull
                                    docker-compose up -d --remove-orphans
                                    
                                    # cleanup unused images to save space
                                    docker image prune -f 
                                    
                                    exit 0
                                    EOF
                                """
                            } catch (Exception e) {
                                echo "SSH Deploy Error: ${e.getMessage()}"
                                error("Failed to deploy to remote server.")
                            }
                        }
                    }    
                }
            }
        }
    }
    post {
        always {
            cleanWs()
        }
    }
}