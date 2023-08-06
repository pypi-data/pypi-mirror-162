import typer
from accomate.aws.route53 import test_dns_list_reply
from accomate.utils.echo import echo
from accomate.utils.wait import run_process_for


def dns_check(hosted_zone_id: str, domains: list):

    auth_service_domain = domains[0]
    store_service_domain = domains[1]
    dns_test_attempts = 0

    replies = test_dns_list_reply(hosted_zone_id, 'A', domains)
    dns_test_attempts = dns_test_attempts + 1
    if replies:
        echo("✅ DNS is verified.")
    else:
        echo(f"✅ Rechecking DNS (attempts: {dns_test_attempts})...")
        run_process_for(10)
        while not test_dns_list_reply(hosted_zone_id, 'A', [auth_service_domain, store_service_domain]):
            echo(f"✅ Rechecking DNS (attempts: {dns_test_attempts})...")
            dns_test_attempts = dns_test_attempts + 1
            run_process_for(10)
            if dns_test_attempts == 10:
                echo("❌ DNS test failed.")
                raise typer.Abort()
        echo("✅ DNS is verified.")
