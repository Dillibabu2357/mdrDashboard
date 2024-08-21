from peewee import *
import yaml
from yaml.loader import SafeLoader
def get_credentials(user):
    dbcredentials = yaml.load(open("db_credentials.yaml"), SafeLoader)
    if user in dbcredentials and 'db' in dbcredentials[user] and 'user' in dbcredentials[user] and 'password' in dbcredentials[user]:
        return dbcredentials[user]['db'], dbcredentials[user]['user'], dbcredentials[user]['password']
    return None, None, None
def get_dburl():
    dbcredentials = yaml.load(open("db_credentials.yaml"), SafeLoader)
    if "database_url" in dbcredentials: return dbcredentials["database_url"]
    return None
db, db_user, db_password = get_credentials('all') # 'information_schema', 'root', 'root123'
if db == None: database = None
else:
    database_url = get_dburl()
    if database_url == None: database = MySQLDatabase(db, **{'charset': 'utf8', 'sql_mode': 'PIPES_AS_CONCAT', 'use_unicode': True, 'port': 3306, 'user': db_user, 'password': db_password})
    else:
        database = MySQLDatabase(db, host=database_url, port=3306, user=db_user, password=db_password)
        print('db url: %s'%database_url)

def getDataQryResults(dbn):
    yamlFile = yaml.load(open("db_credentials.yaml"), SafeLoader)
    keys = {1:'Manuscripts', 2:'Books', 3:'Articles'}
    dictUsers = {}
    jsonKeys = yamlFile['jsonKeys']
    dictDocs = {jsonKeys[dbn]: {'Manuscripts': 0, 'Books': 0, 'Articles': 0, 'Users': 0}}
    txt = 'SELECT "{dbn:s}", DocumentType, COUNT(DocumentType) FROM {dbn:s}.omds_digital_manuscript WHERE isDeleted=0 GROUP BY DocumentType'
    qryDocs = txt.format(dbn=dbn)
    txt = 'SELECT "{dbn:s}", COUNT(*) FROM {dbn:s}.omds_employeemaster WHERE IsDeleted=0'
    qryUsers = txt.format(dbn=dbn)
    cursor = database.execute_sql(qryUsers)
    for row in cursor.fetchall():
        # print('%18s %4d'%(row[0], row[1]))
        dictUsers[row[0]] = row[1]
    # print('%s\n%s\n%18s %s %s'%(qryDocs, 'Documents', 'Database', 'Type', 'Total'))
    cursor = database.execute_sql(qryDocs)
    for row in cursor.fetchall():
        # print('%18s %4d %6d'%(row[0], row[1], row[2]))
        dictDocs[jsonKeys[row[0]]][keys[row[1]]] = row[2]
    for k, v in dictUsers.items(): dictDocs[jsonKeys[k]]['Users'] = v
    # print('Docs\n%s'%dictDocs)
    # cursor = db.execute_sql('SELECT "cedc_mdr" AS "db", DocumentType, COUNT(DocumentType) FROM cedc_mdr.omds_digital_manuscript WHERE isDeleted=0 GROUP BY DocumentType;')
    # res = cursor.fetchone()
    # print('Total: ', res[0])
    return dictDocs


def getDataQryResultsAll():
    yamlFile = yaml.load(open("db_credentials.yaml"), SafeLoader)
    keys = {1:'Manuscripts', 2:'Books', 3:'Articles'}
    dictUsers = {}; dictDocs = {}
    jsonKeys = yamlFile['jsonKeys']; mdrDatabases = list(jsonKeys.keys())
    for dbn in mdrDatabases: dictDocs[jsonKeys[dbn]] = {'Manuscripts': 0, 'Books': 0, 'Articles': 0, 'Users': 0}
    dbn = mdrDatabases[0]
    txt = 'SELECT "{dbn:s}", DocumentType, COUNT(DocumentType) FROM {dbn:s}.omds_digital_manuscript WHERE isDeleted=0 GROUP BY DocumentType'
    qryDocs = txt.format(dbn=dbn)
    txt = 'SELECT "{dbn:s}", COUNT(*) FROM {dbn:s}.omds_employeemaster WHERE IsDeleted=0'
    qryUsers = txt.format(dbn=dbn)
    for dbn in mdrDatabases[1:]:
        txt = ' UNION SELECT "{dbn:s}", DocumentType, COUNT(DocumentType) FROM {dbn:s}.omds_digital_manuscript WHERE isDeleted=0 GROUP BY DocumentType'
        qryDocs += txt.format(dbn=dbn)
        txt = ' UNION SELECT "{dbn:s}", COUNT(*) FROM {dbn:s}.omds_employeemaster WHERE IsDeleted=0'
        qryUsers += txt.format(dbn=dbn)
        dictDocs[jsonKeys[dbn]] = {'Manuscripts': 0, 'Books': 0, 'Articles': 0, 'Users': 0}
    qryDocs += ';'; qryUsers += ';'
    # print('%s\n%s\n%18s %s'%(qryUsers, 'Users', 'Database', 'Total'))
    cursor = database.execute_sql(qryUsers)
    for row in cursor.fetchall():
        # print('%18s %4d'%(row[0], row[1]))
        dictUsers[row[0]] = row[1]
    # print('%s\n%s\n%18s %s %s'%(qryDocs, 'Documents', 'Database', 'Type', 'Total'))
    cursor = database.execute_sql(qryDocs)
    for row in cursor.fetchall():
        # print('%18s %4d %6d'%(row[0], row[1], row[2]))
        dictDocs[jsonKeys[row[0]]][keys[row[1]]] = row[2]
    for k, v in dictUsers.items(): dictDocs[jsonKeys[k]]['Users'] = v
    # print('Docs\n%s'%dictDocs)
    return dictDocs



# def getDataQryResultsAll():
#     yamlFile = yaml.load(open("db_credentials.yaml"), SafeLoader)
#     keys = {1:'Manuscripts', 2:'Books', 3:'Articles'}
#     dictUsers = {}; dictDocs = {}
#     jsonKeys = yamlFile['jsonKeys']; mdrDatabases = list(jsonKeys.keys())
#     for dbn in mdrDatabases: dictDocs[jsonKeys[dbn]] = {'Manuscripts': 0, 'Books': 0, 'Articles': 0, 'Users': 0}
#     dbn = mdrDatabases[0]
#     txt = 'SELECT "{dbn:s}", DocumentType, COUNT(DocumentType) FROM {dbn:s}.omds_digital_manuscript WHERE isDeleted=0 GROUP BY DocumentType'
#     qryDocs = txt.format(dbn=dbn)
#     txt = 'SELECT "{dbn:s}", COUNT(*) FROM {dbn:s}.omds_employeemaster WHERE IsDeleted=0'
#     qryUsers = txt.format(dbn=dbn)
#     for dbn in mdrDatabases[1:]:
#         txt = ' UNION SELECT "{dbn:s}", DocumentType, COUNT(DocumentType) FROM {dbn:s}.omds_digital_manuscript WHERE isDeleted=0 GROUP BY DocumentType'
#         qryDocs += txt.format(dbn=dbn)
#         txt = ' UNION SELECT "{dbn:s}", COUNT(*) FROM {dbn:s}.omds_employeemaster WHERE IsDeleted=0'
#         qryUsers += txt.format(dbn=dbn)
#         dictDocs[jsonKeys[dbn]] = {'Manuscripts': 0, 'Books': 0, 'Articles': 0, 'Users': 0}
#     qryDocs += ';'; qryUsers += ';'
#     # print('%s\n%s\n%18s %s'%(qryUsers, 'Users', 'Database', 'Total'))
#     cursor = database.execute_sql(qryUsers)
#     for row in cursor.fetchall():
#         # print('%18s %4d'%(row[0], row[1]))
#         dictUsers[row[0]] = row[1]
#     # print('%s\n%s\n%18s %s %s'%(qryDocs, 'Documents', 'Database', 'Type', 'Total'))
#     cursor = database.execute_sql(qryDocs)
#     for row in cursor.fetchall():
#         # print('%18s %4d %6d'%(row[0], row[1], row[2]))
#         dictDocs[jsonKeys[row[0]]][keys[row[1]]] = row[2]
#     for k, v in dictUsers.items(): dictDocs[jsonKeys[k]]['Users'] = v
#     # print('Docs\n%s'%dictDocs)
#     return dictDocs






if __name__ == '__main__':
    yamlFile = yaml.load(open("db_credentials.yaml"), SafeLoader)
    mdrDatabases = yamlFile['jsonKeys'].keys()
    print('all: %s\n%s' % (getDataQryResultsAll(), [getDataQryResults(dbn) for dbn in mdrDatabases]))



