class Program:
    def __init__(self, client):
        self.client = client

    def list_program_by_page(self, page=1, per_page=30):
        data = self.client.get('/account/programs', params={'page': page, 'per_page': per_page})
        return data

    def list_all_program(self):
        data = self.client.get('/brm/v1/project/list')
        return data['items']

    def file_accounting(self, project_id):
        data = self.client.get('/brm/v1/file/accounting', params={'projectId': project_id})
        return data
# def delete(self, program_id):
#     data = self.client.post(f'/account/program/{program_id}/del')
#     return data

# def add(self, name, balance=0):
#     params = {'name': name, 'balance': balance}
#     data = self.client.post(f'/account/program/add', data=params)
#     return data

# # kind 1:wallet to program，2:program to wallet
# def charge(self, program_id, amount, kind):
#     params = {'amount': amount, 'kind': kind}
#     data = self.client.post(f'/account/program/{program_id}/charge', data=params)
#     return data
