class Environment:
    def __init__(self, environment):
        self.__environment = environment


    def get_project_and_dataset(self):
        if self.__environment == 'prod':
            return 'propertymanager-385720.real_estates'
        else:
            return 'propertymanager-385720.test_2_real_estates'
