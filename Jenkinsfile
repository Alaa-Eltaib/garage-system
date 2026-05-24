pipeline {
    agent any
    environment {
        repo_url       = 'https://github.com/Alaa-Eltaib/garage-system'
        branch         = 'master'
        sonar_env      = 'SonarQubeServer'
        ser_ip         = 'http://192.168.153.130:9000'
        SonarContainer = 'sonarqube'
    }
    stages {
        stage('Clean Workspace') {
            steps {
                cleanWs()
            }
        }
        stage('Checkout Code') {
            steps {
                git branch: "${env.branch}", url: "${env.repo_url}"
            }
        }
        stage('Docker Compose Down') {
            steps {
                sh 'docker-compose down || true'
                sh 'docker rm -f garage-system || true'
            }
        }
        stage('Docker Compose Up') {
            steps {
                sh 'docker-compose up -d --build'
            }
        }
        stage('Ensure SonarQube Running') {
            steps {
                sh """
                    if [ "\$(docker ps -q -f name=${env.SonarContainer})" ]; then
                        echo "SonarQube is already running"
                    else
                        if [ "\$(docker ps -aq -f name=${env.SonarContainer})" ]; then
                            docker start ${env.SonarContainer}
                        else
                            docker run -d --name ${env.SonarContainer} \
                            -p 9000:9000 --restart=always \
                            -v sonar_data:/opt/sonarqube/data \
                            sonarqube:lts
                        fi
                    fi
                """
                sleep 20
            }
        }
        stage('SonarQube Scan') {
            steps {
                script {
                    def scannerHome = tool 'sonar'
                    def projectName = env.JOB_NAME.replaceAll('/', '_') + "_garage_system"
                    withSonarQubeEnv("${env.sonar_env}") {
                        sh """
                            ${scannerHome}/bin/sonar-scanner \
                            -Dsonar.projectKey=${projectName} \
                            -Dsonar.projectName=${projectName} \
                            -Dsonar.sources=. \
                            -Dsonar.host.url=${env.ser_ip}
                        """
                    }
                }
            }
        }
    }
    post {
        always {
            echo 'Pipeline execution finished.'
        }
    }
}