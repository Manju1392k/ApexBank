"""
Initialize MySQL driver compatibility using PyMySQL if mysqlclient is not natively compiled.
"""
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass
