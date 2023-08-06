def ok(response):
    return {
        'status': 'ok',
        'response': response
    }


def error(response):
    return {
        'status': 'error',
        'response': response
    }
