import os
import sys, argparse

def getOptions(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(description='Function run yaml file datahub')
    parser.add_argument("-d", "--database_name", help="database_name")
    parser.add_argument("--allow", nargs="+", help='list table pattern allow')
    parser.add_argument("--deny", nargs="+", help='list table pattern deny')
    parser.add_argument("--user", help='User name')
    parser.add_argument("--password", help='PassWord')

    options = parser.parse_args(args)
    return options

def create_yaml_file(username, password, database_name, table_pattern_allow = [], table_pattern_deny = []):
    if table_pattern_allow:
        table_pattern_allow_txt = '            allow'
    else:
        table_pattern_allow_txt = ''
    for i in table_pattern_allow:
        table_pattern_allow_txt += "                - " + database_name + '.' + i +'\n'
        
    if table_pattern_deny:
        table_pattern_deny_txt = '            deny'
    else:
        table_pattern_deny_txt = ''
    for i in table_pattern_deny:
        table_pattern_deny_txt += "                - " + database_name + '.' + i +'\n'
        
        
    yaml = f"""
source:
    type: sqlalchemy
    config:
        platform: hive
        connect_uri: "hive://{username}:{password}@master02-dc9c14u41.bigdata.local:10000/{database_name}"
        include_views: False
        table_pattern:
{table_pattern_allow_txt}
            deny:
                - "{database_name}.test.*"
                - "{database_name}.backup_*"
{table_pattern_allow_txt}
        schema_pattern:
            allow:
                - "{database_name}"
            deny:
                - "information_schema"
        options:
            connect_args:
                auth: 'LDAP'
sink:
    type: "datahub-rest"
    config:
        server: "http://gms.datahub.bigdata.local"
    
    """
    
    
    with open(f'datahub_ingest_{database_name}.yaml', 'w') as file:
        file.write(yaml)
    
    return f'datahub_ingest_{database_name}.yaml'
    
def run_yaml_file(yaml_file_name):
    os.system(f'datahub ingest -c {yaml_file_name}')

if __name__ = '__main__':

    options = getOptions()


    yaml_file_name = create_yaml_file(
        username = options.user,
        password = options.password,
        database_name = options.database_name,
        table_pattern_deny=options.deny
    )


    run_yaml_file(yaml_file_name)

