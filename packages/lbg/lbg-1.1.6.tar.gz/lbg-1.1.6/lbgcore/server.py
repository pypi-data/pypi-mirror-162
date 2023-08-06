class Server:
    def __init__(self, client):
        self.client = client

    def list_server(self, program_id):
        data = self.client.get('/brm/v1/node/list', params={'projectId': program_id})
        return data['items']

    def stop(self, machine_id, creator_id):
        data = self.client.post(f'/brm/v1/node/stop/{machine_id}', data={"creatorId": creator_id})
        return data

    def restart(self, machine_id):
        data = self.client.post(f'/brm/v1/node/restart/{machine_id}')
        return data

    def delete(self, machine_id, creator_id):
        data = self.client.post(f'/brm/v1/node/del/{machine_id}', data={"creatorId": creator_id})
        return data

    def create(self, image_id, disk_size, memory, cpu, gpu, program_id, name=None):
        post_data = {
            'imageId': image_id,
            'diskSize': disk_size,
            'projectId': program_id,
            'memory': memory,
            'cpu': cpu,
            'gpu': gpu,
            'name': name
        }
        data = self.client.post(f'/brm/v1/node/add', data=post_data)
        return data

    def to_dev_image(self, machine_id, image_name, comment=''):
        params = {
            'imageName': image_name,
            'nodeId': machine_id,
            'comment': comment
        }
        data = self.client.post(f'/brm/v1/image/add', data=params)
        return data
