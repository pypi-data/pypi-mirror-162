import subprocess


def restart_nginx():
    subprocess.call("sudo systemctl restart nginx", shell=True)
    return True

def verify_nginx_conf():
    subprocess.call("sudo nginx -t", shell=True)
    return True

def add_lets_encrypt_certificate(domain: str, store_email: str):
    # certbot --noninteractive --agree-tos --cert-name ${SITE_TLD} -d ${SITE_DOMAIN_ONE} -d ${SITE_DOMAIN_TWO} -m ${SSL_EMAIL} --webroot -w /var/www/html/
    return subprocess.call(f"sudo certbot --nginx -n --agree-tos -d {domain} -m {store_email}", shell=True)