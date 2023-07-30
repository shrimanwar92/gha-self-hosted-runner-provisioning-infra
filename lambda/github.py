import requests
import sys
import time

class GithubActions():
    def __init__(self, org, repo, pat) -> None:
        self.base_url = f"https://api.github.com/repos/{org}/{repo}"
        #self.base_url = f"https://u9p1035ol8.execute-api.us-east-1.amazonaws.com/v1/repos/{org}/{repo}"
        self.headers = {
            "X-GitHub-Api-Version": "2022-11-28",
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {pat}"
        }

    def get_registration_token(self):
        try:
            response = requests.post(
                url = f"{self.base_url}/actions/runners/registration-token",
                #url = f"{self.base_url}/get-runner-registration-token",
                headers = self.headers
            ).json()
        except BaseException as error:
            print(error)
            sys.exit(1)
        else:
            print(response)
            return response
    
    def get_runner_by_label(self, label):
        runner = None
        
        try:
            response = requests.get(
                url = f"{self.base_url}/actions/runners",
                #url = f"{self.base_url}/get-runners",
                headers = self.headers
            ).json()
        except BaseException as error:
            print(error)
            sys.exit(1)
        else:
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
                    url = f"{self.base_url}/actions/runners/{runner['id']}",
                    #url = f"{self.base_url}/get-runners/{runner['id']}",
                    headers = self.headers
                )
            except BaseException as error:
                print(error)
                sys.exit(1)
            else:
                print(f"Runner with label - {label} deleted successfully")

    def wait_for_runner_registration(self, label):
        timeout_minutes = 5
        retry_interval_seconds = 7
        quiet_period_seconds = 30
        wait_seconds = 0

        print(f"Waiting {quiet_period_seconds}s for the AWS EC2 instance to be registered in GitHub as a new self-hosted runner")
        time.sleep(quiet_period_seconds)
        print(f"Checking every {retry_interval_seconds}s if the GitHub self-hosted runner is registered")

        while wait_seconds <= timeout_minutes * 60:
            runner = self.get_runner_by_label(label)

            if wait_seconds > timeout_minutes * 60:
                print('GitHub self-hosted runner registration error')
                raise TimeoutError(f"A timeout of {timeout_minutes} minutes is exceeded. Your AWS EC2 instance was not able to register itself in GitHub as a new self-hosted runner.")

            if runner and runner['status'] == 'online':
                print(f"GitHub self-hosted runner {runner['name']} is registered and ready to use")
                return
            else:
                wait_seconds += retry_interval_seconds
                time.sleep(retry_interval_seconds)

        raise RuntimeError("The loop should not reach this point. There might be an issue with the logic.")
