import os
import CloudFlare

CLOUDFLARE_TOKEN = os.environ.get("CLOUDFLARE_TOKEN")

cf = CloudFlare.CloudFlare(token=CLOUDFLARE_TOKEN)


def get_zone_id(domain: str):
    """ Get the zone id for a given domain. """
    zones = cf.zones.get(params={'name': domain})
    return zones[0]['id'], zones[0]['name']


def domain_lookup(domain: str, zone_id: str, zone_name: str):
    # check if the sub-domain exists
    try:
        parmas = {
            'name': f"{domain}.{zone_name}",
        }
        dns_records = cf.zones.dns_records.get(zone_id, params=parmas)
        return dns_records
    except CloudFlare.exceptions.CloudFlareAPIError as e:
        return False


def domain_create(slug: str, ip: str, base_domain: str):
    try:
        zone_id, zone_name = get_zone_id(base_domain)
        dns_records = domain_lookup(slug, zone_id, zone_name)
        if dns_records:
            print(f"Domain {slug} already exists.")
            return
        else:
            print(f"Creating domain {slug}...")
            dns_record = {
                'type': 'A',
                'name': f"{slug}.{zone_name}",
                'content': ip
            }
            cf.zones.dns_records.post(zone_id, data=dns_record)

    except CloudFlare.exceptions.CloudFlareAPIError as e:
        return False


def domain_delete(domain: str):
    pass

def setup_domains_for_services(client_name: str):
    pass