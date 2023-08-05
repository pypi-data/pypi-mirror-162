class APIException(Exception):
    def __init__(self, status, message, type):
        self.status = status
        self.message = message
        self.type = type
        self.description = self.get_descriptions(status, type)

    def get_descriptions(self, status, type):
        if(type == "user"):
            if(status == 401):
                return "Invalid API Key."
            elif(status == 412):
                return "Missing parameter."
            elif(status == 413):
                return "Database networking issues."
            elif(status == 414):
                return "Invaild user info."
            elif(status == 415):
                return "Not a registered user."
            else: # status 500
                return "Other errors occurred."
        elif(type == "banner"):
            if(status == 400):
                return "No required input values."
            else: # status 500
                return "Elasticsearch failed."
        elif(type == "domain"):
            if(status == 400):
                return "Invalid URL."
            elif(status == 412):
                return "Insufficient parameters."
            elif(status == 420):
                return "Inconsistent parameters."
            else: # status 500
                return "errors within server."
        else:
            return "No Description"

    def __str__(self):
        return self.message + " : " + self.description