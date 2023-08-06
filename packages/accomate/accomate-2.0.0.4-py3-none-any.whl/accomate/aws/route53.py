import boto3

route53 = boto3.client('route53')


def get_hosted_zone_id(domain: str):
    try:
        response = route53.list_hosted_zones()
        hosted_zones = response['HostedZones']
        for hosted_zone in hosted_zones:
            if hosted_zone['Name'] == f"{domain}.":
                return hosted_zone['Id']
        raise Exception("Hosted zone not found")
    except Exception as e:
        raise Exception("Hosted Zone ID failed: {}".format(e))


def list_dns_records(hosted_zone_id: str):
    try:
        response = route53.list_resource_record_sets(
            HostedZoneId=hosted_zone_id)
        return response['ResourceRecordSets']
    except Exception as e:
        raise Exception("DNS Record list failed: {}".format(e))


def verify_dns_record(hosted_zone_id: str, record_type: str, record_name: str, record_value: str):
    try:
        record_type = record_type.strip()
        record_name = record_name.strip()
        record_value = record_value.strip()
        records = list_dns_records(hosted_zone_id)
        for record in records:
            if record['Type'] == record_type and record['Name'] == f"{record_name}." and record['ResourceRecords'][0]['Value'] == record_value:
                return True
        return False
    except Exception as e:
        raise Exception("DNS Record verify failed: {}".format(e))


def add_dns_record(hosted_zone_id: str, record_type: str, record_name: str, record_value: str):
    try:
        response = route53.change_resource_record_sets(HostedZoneId=hosted_zone_id, ChangeBatch={
            'Changes': [{
                'Action': 'CREATE',
                'ResourceRecordSet': {
                    'Name': record_name,
                    'Type': record_type,
                    'TTL': 300,
                    'ResourceRecords': [{
                        'Value': record_value
                    }]
                }
            }]
        })
        return response
    except Exception as e:
        raise Exception("DNS Record add (Action) failed: {}".format(e))


def test_dns_reply(hosted_zone_id: str, record_type: str, record_name: str):
    try:
        response = route53.test_dns_answer(
            HostedZoneId=hosted_zone_id,
            RecordName=record_name,
            RecordType=record_type,
        )
        return response['ResponseMetadata']['HTTPStatusCode'] == 200
    except Exception as e:
        raise Exception("DNS Reply failed: {}".format(e))


def test_dns_list_reply(hosted_zone_id: str, record_type: str, record_names: list):
    try:
        responses = []
        for record_name in record_names:
            response = route53.list_resource_record_sets(
                HostedZoneId=hosted_zone_id,
                StartRecordName=record_name,
                StartRecordType=record_type,
            )
            responses.append(response['ResponseMetadata']
                             ['HTTPStatusCode'] == 200)
        return True if False not in responses else False
    except Exception as e:
        raise Exception("DNS List Reply failed: {}".format(e))
