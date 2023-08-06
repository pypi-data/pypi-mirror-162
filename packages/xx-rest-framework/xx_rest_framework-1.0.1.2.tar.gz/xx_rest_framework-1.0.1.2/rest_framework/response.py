from tornado.web import RequestHandler


class Response:
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f"{self.__class__} message: {self.message}"


if __name__ == '__main__':
    response = Response("hello")
    print(response)
