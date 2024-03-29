def BuildBadge = addEmbeddableBadgeConfiguration(id: "build", subject: "Build")
def TestBadge = addEmbeddableBadgeConfiguration(id: "test", subject: "Test")

pipeline {
    options {
    // the variable $WORKSPACE is assigned dynamically at the beginning of every stage
    // and might change depending on the number of concurrent builds active.
    // We can only allow 1 concurrent build to have a consistent access to $WORKSPACE
    // Otherwise we should use stash/unstash for the miniconda installation
        disableConcurrentBuilds()
    }
    environment {
       EMAIL_TO_1 = 'victoria.cherkas@meteoswiss.ch'
       EMAIL_TO_2 = 'victoria.cherkas@meteoswiss.ch'
       CONDA_ENV_NAME = 'iconarray'
    }
    agent none
    stages {
        stage('Setup') {
            parallel {
                stage('setup miniconda on daint') {
                    agent { label 'daint' }
                    environment {
                        PATH = "$WORKSPACE/miniconda_$NODE_NAME/bin:$PATH"
                    }
                    steps {
                        script {
                            BuildBadge.setStatus('running')
                        }
                        sh './setup.sh'
                    }
                    post {
                        failure {
                            echo 'Cleaning up workspace'
                            deleteDir()
                        }
                    }
                }
                stage('setup miniconda on tsa') {
                    agent { label 'tsa' }
                    environment {
                        PATH = "$WORKSPACE/miniconda_$NODE_NAME/bin:$PATH"
                    }
                    steps {
                        script {
                            BuildBadge.setStatus('running')
                        }
                        sh './setup.sh'
                    }
                    post {
                        failure {
                            echo 'Cleaning up workspace'
                            deleteDir()
                        }
                    }
                }
            }
            post {
                failure {
                    node('tsa') {
                        script {
                            BuildBadge.setStatus('failing')
                        }
                    }
                }
                success {
                    node('tsa') {
                        script {
                            BuildBadge.setStatus('passing')
                        }
                    }
                }
            }
        }
        stage('Test') {
            parallel {
                stage('test on daint') {
                    agent { label 'daint' }
                    environment {
                        PATH = "$WORKSPACE/miniconda_${NODE_NAME}/bin:$PATH"
                    }
                    steps {
                        script {
                            TestBadge.setStatus('running')
                        }
                        sh './test.sh'
                    }
                    post {
                        success {
                            mail bcc: '',
                            body: "<b>Jenkins Success</b><br>Project: ${env.JOB_NAME}<br>Build Number: ${env.BUILD_NUMBER}<br>Build URL: ${env.BUILD_URL}" ,
                            cc: "${EMAIL_TO_2}", charset: 'UTF-8', from: '', mimeType: 'text/html',
                            replyTo: '', subject: "Jenkins Job Success ${NODE_NAME} ->${env.JOB_NAME}",
                            to: "${EMAIL_TO_1}";
                        }
                        failure {
                            script {
                                mail bcc: '',
                                body: "<b>Jenkins Failure</b><br>Project: ${env.JOB_NAME}<br>Build Number: ${env.BUILD_NUMBER}<br>Build URL: ${env.BUILD_URL}" ,
                                cc: "${EMAIL_TO_2}", charset: 'UTF-8', from: '', mimeType: 'text/html',
                                replyTo: '', subject: "Jenkins Job Failure ${NODE_NAME} -> ${env.JOB_NAME}",
                                to: "${EMAIL_TO_1}";
                            }

                        }
                        always {
                            archiveArtifacts artifacts: '*.log', allowEmptyArchive: true
                            echo 'Cleaning up workspace'
                            deleteDir()
                        }
                    }
                }
                stage('test on tsa') {
                    agent { label 'tsa' }
                    environment {
                        PATH = "$WORKSPACE/miniconda_${NODE_NAME}/bin:$PATH"
                    }
                    steps {
                        script {
                            TestBadge.setStatus('running')
                        }
                        sh './test.sh'
                    }
                    post {
                        success {
                            mail bcc: '',
                            body: "<b>Jenkins Success</b><br>Project: ${env.JOB_NAME}<br>Build Number: ${env.BUILD_NUMBER}<br>Build URL: ${env.BUILD_URL}" ,
                            cc: "${EMAIL_TO_2}", charset: 'UTF-8', from: '', mimeType: 'text/html',
                            replyTo: '', subject: "Jenkins Job Success ${NODE_NAME} ->${env.JOB_NAME}",
                            to: "${EMAIL_TO_1}";
                        }
                        failure {
                            mail bcc: '',
                            body: "<b>Jenkins Failure</b><br>Project: ${env.JOB_NAME}<br>Build Number: ${env.BUILD_NUMBER}<br>Build URL: ${env.BUILD_URL}" ,
                            cc: "${EMAIL_TO_2}", charset: 'UTF-8', from: '', mimeType: 'text/html',
                            replyTo: '', subject: "Jenkins Job Failure ${NODE_NAME} -> ${env.JOB_NAME}",
                            to: "${EMAIL_TO_1}";
                        }
                        always {
                            archiveArtifacts artifacts: '*.log', allowEmptyArchive: true
                            echo 'Cleaning up workspace'
                            deleteDir()
                        }
                    }
                }
            }
            post {
                failure {
                    node('tsa') {
                        script {
                            TestBadge.setStatus('failing')
                        }
                    }
                }
                success {
                    node('tsa') {
                        script {
                            TestBadge.setStatus('passing')
                        }
                    }
                }
            }
        }
    }
    post { 
        always { 
            node('tsa') {
                deleteDir()
            }
        }
    }
}
