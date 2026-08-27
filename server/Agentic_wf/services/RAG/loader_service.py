from Agentic_wf.config import Loader



class LoaderService:

    # def __init__(self, ):
    #     self.file_path = file_path

    def load(self,file_path: str):
        return Loader.load(file_path)
