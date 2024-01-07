from api.http_.mail.tasks import app

if __name__ == '__main__':
    argv = [
        'worker',
        '--loglevel=INFO',
        '--pool=solo',  # Было сказано, что на Windows есть некий баг, который избегается этим параметром.
    ]
    app.worker_main(argv)
