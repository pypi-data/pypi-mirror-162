def validate_project_config(json: dict) -> bool:

    env = json.get('environment')

    possible_envs = ['dev', 'production']

    if not json:
        raise Exception("No project config found!")
    if not json.get('store'):
        raise Exception("No store found!")
    else:
        if not json['store'].get('name'):
            raise Exception("No store name found!")
        if not json['store'].get('slug'):
            raise Exception("No store slug found!")
        if not json['store'].get('email'):
            raise Exception("No store email found!")
        if not json['store'].get('template'):
            raise Exception("No store template found!")
    if env not in possible_envs:
        raise Exception("No valid environment found!")
    if not json.get('service_version'):
        raise Exception("No service version found!")
    if not json.get('urls'):
        raise Exception("No urls found!")
    else:
        if not json['urls'].get('store_service'):
            raise Exception("No store service url found!")
        if not json['urls'].get('auth_service'):
            raise Exception("No auth service url found!")
    if not json.get('ports'):
        raise Exception("No ports found!")
    else:
        if not json['ports'].get('store_service'):
            raise Exception("No store service port found!")
        if not json['ports'].get('auth_service'):
            raise Exception("No auth service port found!")
    return True
