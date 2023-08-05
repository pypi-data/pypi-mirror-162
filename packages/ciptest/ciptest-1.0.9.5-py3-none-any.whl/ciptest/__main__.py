import click
import os
import os.path
from ciptest.client_api import CIP
from ciptest.func import *
from ciptest.cip_exceptions import *

@click.group()
def main():
    pass

@main.command()
@click.argument("KEY")
def init(key):
    '''Command for Initializing Criminal IP CLI\n
    KEY : YOUR API KEY <- Find on
    "https://www.criminalip.io/ko/mypage/information"'''
    dir = os.path.expanduser("~/.CIP/")
    if not os.path.isdir(dir):
        try:
            os.makedirs(dir)
        except OSError:
            raise click.ClickException("Unable to create directory.")
    key = key.strip()
    api = CIP(key)
    try:
        api.user_me()
    except APIException as e:
        click.echo(click.style(e, fg='red'))
        click.echo(click.style("Please Check Your API Key.", fg='red'))
    
    key_path = dir + 'key'
    with open(key_path, 'w') as f:
        f.write(key)
        click.echo("Successfully Initialized")
    os.chmod(key_path, 0o600)

@main.command()
def info():
    """Command for Inquiring about user information."""
    key = get_key()
    api = CIP(key)
    try:
        click.echo(json_prints(api.user_me()))
    except APIException as e:
        click.echo(click.style(e, fg='red'))

# Commands With IP Search
@main.command()
@click.argument('ip')
@click.option('--mode',
    help='''Choose IP Search Mode\n
            data - returns all IP information\n
            summary - provides only the country and score information for IP\n
            vpn - VPN IP Detection Information Inquery\n
            hosting - Hosting IP Detection Information Inquery\n''')
@click.option('--full', is_flag=False, flag_value=False, type=click.BOOL,
    help = '''[Only For Mode Data/Hosting]\nReturn full data if value is "full:true", return up to 20 data 
            if value is "full:false" or without "full" parameter''')
def ip(mode, ip, full):
    """Commands Related to IP Searching.\n
        ip : Search target IP Address"""
    key = get_key()
    api = CIP(key)
    params = {"ip" : ip, "full" : full}
    if mode == "data":
        save_results("IP_DATA_{}".format(ip), json_prints(api.ip_data(params)))
    elif mode == "summary":
        save_results("IP_SUMMARY_{}".format(ip), json_prints(api.ip_summary(params)))
    elif mode == "vpn":
        save_results("IP_VPN_{}".format(ip), json_prints(api.ip_vpn(params)))
    elif mode == "hosting":
        save_results("IP_HOSTING_{}".format(ip), json_prints(api.ip_hosting(params)))
    else:
        ctx = click.get_current_context()
        click.echo(click.style("Please Enter Right Mode", fg='red'))
        click.echo(ctx.get_help())
        ctx.exit()
    click.echo(click.style("Result Successfully Stored.\nResult In ~/CIP_results/", fg='green'))

# Commands with Banner Search
@main.command()
@click.argument("Query")
@click.option("--mode",
    help = '''Choose Banner Search Mode\n
            search - searching banner_data with filter\n
            stats - Statistics for banner_data search\n''')
@click.option('--offset', type=click.INT, default=0, 
    help = '[Only For Banner Search]\nStarting position in the dataset(entering in increments of 10).\ndefault is 0.')
def banner(mode, query, offset):
    """Commands Related to Banner Searching.\n
        QUERY : Original searching text containing filters."""
    key = get_key()
    api = CIP(key)
    params = {"query" : query, "offset" : offset}
    try:
        if mode == "search":
            save_results("BANNER_SEARCH_{}".format(query), json_prints(api.banner_search(params)))
        elif mode == "stats":
            save_results("BANNER_STATS_{}".format(query), json_prints(api.banner_stats(params)))
        else:
            ctx = click.get_current_context()
            click.echo(click.style("Please Enter Right Mode", fg='red'))
            click.echo(ctx.get_help())
            ctx.exit()
    except APIException as e:
        click.echo(click.style(e, fg='red'))
    click.echo(click.style("Result Successfully Stored.\nResult In ~/CIP_results/", fg='green'))

# Commands With Domain Search
@main.command()
@click.argument("param")
@click.option("--mode",
    help = '''Choose Domain Search Mode\n
            reports - When a users requests a domain search, return the scan_id of an existing report, or scan_id of a report starting a new scan, according to the relevant search results.\n
            report - When the users wants to query the report data for a specific scan_id, return the data.\n
            scan - API used by users to perform a new domain scan. Returns the scan_id of the report in the relevant request.\n''')
def domain(mode, param):
    """Commands Related to Domain Searching.\n
        [Param]\nQUERY : Domain Search Query\n
        (Only for report mode) Scan ID : Domain Scan ID From domain-scan or domain-reports"""
    key = get_key()
    api = CIP(key)
    params = {"query" : param}
    try:
        if mode == "reports":
            save_results("DOMAIN_REPORTS_{}".format(param), json_prints(api.domain_reports(params)))
        elif mode == "report":
            save_results("DOMAIN_REPORT_ID_{}".format(param), json_prints(api.domain_report_id(param)))
        elif mode == "scan":
            save_results("DOMAIN_SCAN_{}".format(param), json_prints(api.domain_scan(params)))
        else:
            ctx = click.get_current_context()
            click.echo(click.style("Please Enter Right Mode", fg='red'))
            click.echo(ctx.get_help())
            ctx.exit()
    except APIException as e:
        click.echo(click.style(e, fg='red'))
    click.echo(click.style("Result Successfully Stored.\nResult In ~/CIP_results/", fg='green'))

if __name__ == '__main__':
    main()
