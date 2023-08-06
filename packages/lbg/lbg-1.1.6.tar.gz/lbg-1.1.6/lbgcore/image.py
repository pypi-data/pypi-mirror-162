class Image:
    def __init__(self, client):
        self.client = client

    def list_image_by_page(self, program_id, kind=None, page=1, per_page=30):
        params = {'page': page, 'pageSize': per_page, 'projectId': program_id, "type": "all"}
        if kind is not None:
            params['kind'] = kind
        data = self.client.get('/brm/v1/image/list', params=params)
        return data

    def list_all_image(self, program_id, kind=None):
        program_list = []
        data = self.list_image_by_page(program_id, kind=kind)
        total = data['total']
        per_page = data['pageSize']
        page_number = 0
        while page_number * per_page < total:
            page_number = page_number + 1
            if page_number > 1:
                data = self.list_image_by_page(program_id, kind=kind, page=page_number, per_page=30)
            program_list.extend(data['items'])
        return program_list

    def delete(self, image_id):
        data = self.client.post(f'/brm/v1/image/del/{image_id}')
        return data

    def release(self, image_id, program_id, name, comment=''):
        if not name:
            raise ValueError("image name can not be empty")
        params = {
            'program_id': program_id,
            'imageName': name,
            'comment': comment
        }
        data = self.client.post(f'/brm/v1/image/release/{image_id}', data=params)
        return data
