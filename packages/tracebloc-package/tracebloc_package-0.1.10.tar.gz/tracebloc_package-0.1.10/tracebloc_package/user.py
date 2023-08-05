# import useful libraries
import getpass
import requests
import json
import getpass, os
from .upload import Model
from .linkModelDataSet import LinkModelDataSet
from termcolor import colored
import rich


class User:
    """
    Parameters: username, password

    ***
    Please provide a valid username and password
    Call getToken method on Login to get new token for provided
    username and password
    """

    def __init__(self, environment="production"):
        self.__environment = environment
        self.__url = self.env_url(self.__environment)
        if self.__url is None:
            text = colored(
                "\nThe class does not take any arguments. Just run: user = User()",
                "red",
            )
            print(text, "\n")
            return
        self.__username = input("Enter your email address : ")
        self.__password = getpass.getpass("Enter your password : ")
        self.__token = self.login()
        if self.__token is None or self.__token == "":
            # text = colored(
            #     "You are not logged in. Please go back to ‘1. Connect to Tracebloc’ and proceed with logging in.",
            #     "red",
            # )
            # print(text, "\n")
            return
        self.__modelId = ""
        self.__modelName = ""
        self.__weights = False

    def env_url(self, environment="production"):
        url = None
        if environment == "development":
            url = "https://xray-backend-develop.azurewebsites.net/"
        if environment == "ds":
            url = "https://xray-backend.azurewebsites.net/"
        elif environment == "staging":
            url = "https://xray-backend-staging.azurewebsites.net/"
        elif environment == "" or environment == "production":
            url = "https://tracebloc.azurewebsites.net/"
        return url

    def login(self):
        """Function to get Token for username provided"""
        r = requests.post(
            f"{self.__url}api-token-auth/",
            data={"username": self.__username, "password": self.__password},
        )
        if r.status_code == 200:
            print(f"\nLogged in as {self.__username}")
            token = json.loads(r.text)["token"]
            return token
        else:
            print("\n")
            text = colored(
                "Login credentials are not correct. Please try again.", "red",
            )
            print(text, "\n")
            return ""

    def logout(self):
        """Call this to logout from current sesion"""
        try:
            header = {"Authorization": f"Token {self.__token}"}
            r = requests.post(f"{self.__url}logout/", headers=header)
            if r.status_code == 200:
                self.__token = None
                print("You have been logged out.")
            else:
                print("Logout Failed. Retry!")
        except Exception as e:
            print("Logout Failed. Retry!")

    def uploadModel(self, modelname: str, weights=False):

        """
        Make sure model file and weights are in current directory
        Parameters: modelname

        modelname: model file name eg: vggnet, if file name is vggnet.py
        weights: upload pre trained weights if set True. Default: False

        *******
        return: model unique Id
        """
        try:
            if self.__token == "" or self.__token == None:
                text = colored(
                    "You are not logged in. Please go back to ‘1. Connect to Tracebloc’ and proceed with logging in.",
                    "red",
                )
                print(text, "\n")
                return
            if weights:
                self.__weights = weights
            else:
                self.__weights = False
            self.__modelName = modelname
            model = Model(self.__modelName, self.__token, self.__weights, self.__url)
            self.__modelId, self.__modelName = model.getNewModelId()
            if self.__modelId == "" or self.__modelId is None:
                text = colored(f"'{self.__modelName}' upload Failed.", "red")
                print(text, "\n")
                self.__weights = False
                return
            else:
                text = colored(f"'{self.__modelName}' upload successful.", "green")
                print(text, "\n")

        except:
            return

    def linkModelDataset(self, datasetId: str):

        """
        Role: Link and checks model & datasetId compatibility
              create training plan object

        parameters: modelId, datasetId
        return: training plan object
        """
        try:
            if self.__token == "" or self.__token is None:
                text = colored(
                    "You are not logged in. Please go back to ‘1. Connect to Tracebloc’ and proceed with logging in.",
                    "red",
                )
                print(text, "\n")
                return None
            if self.__modelId == "" or self.__modelId is None:
                text = colored(
                    "Model not uploaded. Please first upload the model.", "red"
                )
                print(text, "\n")
                return None
            if self.__checkmodel(datasetId):
                return LinkModelDataSet(
                    self.__modelId,
                    datasetId,
                    self.__token,
                    self.__weights,
                    self.__total_images,
                    self.__num_classes,
                    self.__url,
                    self.__environment,
                )
            else:
                return None
        except:
            text = colored("Model Link Failed!", "red")
            print(text, "\n")

    def __checkmodel(self, datasetId):
        try:
            header = {"Authorization": f"Token {self.__token}"}
            re = requests.post(
                f"{self.__url}check-model/",
                headers=header,
                data={"datasetId": datasetId, "modelName": self.__modelId, "type": 'linking_dataset'},
            )
            if re.status_code == 403 or re.status_code == 400:
                text = colored(
                    f"There is no dataset with ID: {datasetId} in your dataset table.\n"
                    f"Please check your dataset ID.",
                    "red",
                )
                print(text)
                return False
            elif re.status_code == 202 or re.status_code == 200:
                body_unicode = re.content.decode("utf-8")
                content = json.loads(body_unicode)
                if content["status"] == "failed":
                    text = colored("Assignment failed!", "red")
                    print(text, "\n")
                    print(f"DataSet '{datasetId}' expected parameters :")
                    print(
                        f"classes : {content['datasetClasses']}, shape: {content['datasetShape']}\n"
                    )
                    print(f"'{self.__modelName}' parameters :")
                    print(
                        f"classes : {content['outputClass']}, shape: {content['inputShape']}\n"
                    )
                    print(
                        "Please change model parameters to match expected dataset parameters."
                    )
                    return False
                elif content["status"] == "passed":
                    text = colored("Assignment successful!", "green")
                    print(text, "\n")
                    print("Please set training plan.")
                    self.__total_images = content["total_images"]
                    self.__num_classes = content["datasetClasses"]
                    return True
            else:
                text = colored(f"Error Occured. Linking Failed!", "red")
                print(text)
                return False
        except:
            text = colored(f"Communication Fail Error!", "red")
            print(text)
            return False

    def help(self):
        print(
            "User is a method in this package which authenticates the user, provides access to Tracebloc, lets you upload your model, set the training plan and more.\n"
        )

        print("Only registered Users are allowed to access this package.\n")

        print("In order to authenticate, run cell.")

        print("Enter email register on tracebloc and password.\n")

        print("Other user attributes are uploadModel() and linkModelDataset()\n")

        print("uploadModel():")
        print("This helps user to upload a compatible model and weights.\n")

        print("linkModelDataset():")
        print("Link uploaded model with a dataset.\n")

        rich.print(
            "For more information check the [link=https://docs.tracebloc.io/user-uploadModel]docs[/link]"
        )
