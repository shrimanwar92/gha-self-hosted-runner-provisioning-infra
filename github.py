import requests

class GithubActions():
    def __init__(self, pat) -> None:
        #self.base_url = f"https://api.github.com/orgs/org-nilay-shrimanwar"
        self.base_url = "https://tce5rsec11.execute-api.us-east-1.amazonaws.com/v1"
        self.headers = {
            "X-GitHub-Api-Version": "2022-11-28",
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {pat}"
        }

    def get_registration_token(self):
        try:
            response = requests.post(
                #url = f"{self.base_url}/actions/runners/registration-token",
                url = f"{self.base_url}/get-runner-registration-token",
                headers = self.headers
            ).json()
        except BaseException as error:
            print(error)
        else:
            return response
    
    def get_runner_by_label(self, label):
        runner = None
        
        try:
            response = requests.get(
                #url = f"{self.base_url}/actions/runners",
                url = f"{self.base_url}/get-runners",
                headers = self.headers
            ).json()
        except BaseException as error:
            print(error)
        else:
            print(response)
            if response['total_count'] != 0:
                for rnr in response['runners']:
                    for rnr_lbl in rnr['labels']:
                        if rnr_lbl['name'] == label:
                            runner = rnr

        return runner
    
    def remove_runner(self, label):
        runner = self.get_runner_by_label(label)

        if runner == None:
            return
        else:
            try:
                requests.delete(
                    #url = f"{self.base_url}/actions/runners/{runner['id']}",
                    url = f"{self.base_url}/get-runners/{runner['id']}",
                    headers = self.headers
                )
            except BaseException as error:
                print(error)
            else:
                print(f"Runner with label - {label} deleted successfully")