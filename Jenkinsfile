node {

    def python

    sh 'mkdir -p ./_ci_repository'
    dir('./_ci_repository') {
        git url: 'https://github.com/ihiji/ci', credentialsId: 'ihiji-chef-api-key-as-uname-pw'
        dir ('./jenkins') {
            python = fileLoader.load('./python.groovy')
            python.repo = 'django-fields'
            python.loadFiles()
        }
    }


    checkout scm

    try {
        stage('Build') {
            python.build()
        }

        withEnv(['DOCKER_EXEC_ARGS=-T']){
            stage('Test') {
                python.test()
            }
        }
        stage('Deploy') {
            if (env.BRANCH_NAME == 'development' || env.BRANCH_NAME == 'master') {
                python.deploy()
            }
        }
    }
    catch (e) {
        currentBuild.result = 'FAILED'
        throw e as java.lang.Throwable
    }
    finally {
        python.checkBuild()
    }
}