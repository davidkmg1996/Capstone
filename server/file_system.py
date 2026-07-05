class FileSystem:
    def __init__(self):
        self.root = {}
        self.current_folder = None

    def create_folder(self):

        pass

    def get_file(self):
        pass

    def rename_file(self):
        pass

    def delete_file(self):
        pass

# user will pass some identifier to our api
# our api will then look for the file in our postgre by the identifier that was passed through sqlalchemy
# sqlalchemy will then return the file (could be a folder or a report)
# our api will then send back the file as an http response

'''
    PostgreSQL

    Table
        User
        File
'''
