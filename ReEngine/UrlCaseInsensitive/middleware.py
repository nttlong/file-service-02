from django.shortcuts import redirect
def ResolveCaseInsesitive(input_hadler):
     ret= ResolveCaseInsesitiveHandler(input_hadler)
     return ret.handle_request

class ResolveCaseInsesitiveHandler(object):
    def __init__(self,input_handler):
        self.input_handler=input_handler
    def handle_request(self, request):
        request.path == request.path.lower()
        if request.path == request.path.lower():
            return self.input_handler(request)
        return redirect(request.path.lower())
