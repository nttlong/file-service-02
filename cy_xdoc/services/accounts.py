import cy_kit
from cy_xdoc.repos.accounts import Accounts


class AccountService:
    def __init__(self, repo: Accounts = cy_kit.single(Accounts)):
        self.repo: Accounts = repo
