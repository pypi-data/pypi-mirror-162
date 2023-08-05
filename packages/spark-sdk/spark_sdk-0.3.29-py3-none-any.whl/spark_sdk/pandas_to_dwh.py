import os
import sys
from .utils import choose_num_core, choose_executor_memory, choose_driver_memory, _check_series_convert_timestamps_internal, _get_local_timezone, contains_duplicates
from .hive_metastore import HiveMetastoreClient

# for yarn support
os.environ['SPARK_HOME'] = "/opt/spark/spark-3.0.2-bin-hadoop2.7/"
os.environ['JAVA_HOME'] = "/usr/jdk64/jdk1.8.0_112/"
os.environ['SPARK_CONF_DIR'] = ""


import findspark
findspark.init("/opt/spark/spark-3.0.2-bin-hadoop2.7/")

# Install latest Pyarrow version
import os
import subprocess
from pyarrow import fs
import pyarrow.parquet as pq
import pyarrow as pa
import pandas as pd

os.environ['HADOOP_CONF_DIR'] = "/etc/hadoop/conf/"
os.environ['JAVA_HOME'] = "/usr/jdk64/jdk1.8.0_112"
os.environ['HADOOP_HOME'] = "/usr/hdp/3.1.0.0-78/hadoop"
os.environ['ARROW_LIBHDFS_DIR'] = "/usr/hdp/3.1.0.0-78/usr/lib/"
os.environ['CLASSPATH'] = subprocess.check_output("$HADOOP_HOME/bin/hadoop classpath --glob", shell=True).decode(
    'utf-8')

hdfs = fs.HadoopFileSystem(host="hdfs://hdfs-cluster.datalake.bigdata.local", port=8020)

import json
import sys

if not sys.warnoptions:
    import warnings
    warnings.simplefilter("ignore")


class Utf8Encoder(object):
    def __init__(self, fp):
        self.fp = fp

    def write(self, data):
        if not isinstance(data, bytes):
            data = data.encode('utf-8')
        self.fp.write(data)

        
# display options
try:
    import IPython
    IPython.auto_scroll_threshold = 2000

    from IPython.core.interactiveshell import InteractiveShell
    InteractiveShell.ast_node_interactivity = "all"
    from IPython.display import display

    from IPython.core.display import HTML
    display(HTML("<style>pre { white-space: pre !important; }</style>"))

except Exception as e:
    print(e)

pd.options.display.max_columns = 50


from typing import (Union)

class PySpark:
    def __init__(self, driver_memory='1G', num_executors='1', executor_memory='1G', port='', yarn=False):
        """
         Parameters
        ----------

        driver_memory: memory for spark driver and executor memory, must less than 8Gb. 8Gb is handle table 10 milion rows
        executor_memory: memeory for core spark, must less than 8G
        core: executor core, must less than 10 cores
        port: change port if user false job
        yarn: (boolan) if True is run with yarn mode, if False run with local mode
        """

        self.driver_memory = driver_memory
        self.executor_memory = executor_memory
        self.num_executors = num_executors
        self.port = port

        if yarn:
            self.yarn = 'yarn'
        else:
            self.yarn = f'local[{self.num_executors}]'

        # create spark session
        import pyspark
        from pyspark import SparkConf
        from pyspark.sql import SparkSession
        from pyspark.sql import SQLContext

        conf = SparkConf()

        # config spark application name
        import getpass
        conf.setAppName(f"spark_sdk_{getpass.getuser()}")

        # config location for spark finding metadata from hive metadata server
        conf.set("hive.metastore.uris",
                 "thrift://master01-dc9c14u40.bigdata.local:9083,thrift://master02-dc9c14u41.bigdata.local:9083")
        conf.set("spark.sql.hive.metastore.jars", "/opt/spark/spark-3.0.2-bin-hadoop2.7/*")

        # config directory to use for "scratch" space in Spark, including map output files and RDDs that get stored on disk
        if os.path.exists('./tmp/'):
            pass
        else:
            os.mkdir('./tmp/')
        conf.set('spark.local.dir', './tmp/')
        # config in-memory columnar data format that is used in Spark to efficiently transfer data between JVM and Python processes
        conf.set("spark.kryoserializer.buffer.max", "2000")
        conf.set("spark.sql.execution.arrow.pyspark.enabled", "true")
        conf.set("spark.sql.execution.arrow.enabled", "true")
        conf.set("spark.sql.execution.arrow.maxRecordsPerBatch", "10000")
        
        if self.yarn == 'yarn':
           # config spark dynamicAllocation
            conf.set("spark.dynamicAllocation.enabled", "true")
            conf.set("spark.dynamicAllocation.shuffleTracking.enabled", "true")
            conf.set("spark.dynamicAllocation.minExecutors", "1")
            conf.set("spark.dynamicAllocation.maxExecutors", "8")
            conf.set("spark.dynamicAllocation.executorIdleTimeout", "300s")
            conf.set("spark.dynamicAllocation.shuffleTracking.enabled", "true")
            conf.set("spark.dynamicAllocation.shuffleTracking.timeout", "300s")

        # config partition Size
        # conf.set('spark.sql.adaptive.coalescePartitions.minPartitionSize', '128MB')
        conf.set('spark.sql.files.minPartitionNum', 100000)

        # config spark driver memory
        conf.set("spark.driver.memory", self.driver_memory)
        conf.set('spark.executor.memory', self.executor_memory)
        conf.set('spark.driver.maxResultSize', '10G')


        if int(self.num_executors) > 1:
            conf.set('num-executors', self.num_executors)
            conf.set('executor-cores', 4)
        conf.set('spark.rpc.message.maxSize', '700')

        # conf.set("spark.ui.enabled", "false")
        if not port:
            port = 0
            for j,i in enumerate(getpass.getuser()):
                port+=ord(i) * 1 if j//2 == 1 else -1
            port +=4000
        conf.set("spark.ui.port", port)

        # config for write append parquet
        conf.set("spark.sql.parquet.compression.codec", "snappy")

        # set metastore.client.capability.check to false
        conf.set("hive.metastore.client.capability.check", "false")

        # config for descrypt data
        conf.set("spark.jars", "hdfs:///shared/jars/hotpot_2.12-0.0.3.jar")
        conf.set("spark.sql.redaction.string.regex", ".{22}==")

        self.spark = SparkSession.builder.config(conf=conf).master(self.yarn).enableHiveSupport().getOrCreate()
        # print("Spark UI URL %s" % self.spark.sparkContext.uiWebUrl)

        # config timezone
        self.spark.conf.set('spark.sql.session.timeZone', '+07:00')

        # config show pandas dataframe format on notebook
        self.spark.conf.set("spark.sql.repl.eagerEval.enabled", True)
        self.spark.conf.set("spark.sql.repl.eagerEval.truncate", 200)

        self.spark.conf.get("hive.metastore.uris")

        # defing decrypt function
        self.spark._jvm.vn.fpt.insights.utils.Helper.registerUdf("fdecrypt", "fdecrypt")
        self.spark._jvm.vn.fpt.insights.utils.Helper.registerUdf("fencrypt", "fencrypt")
        
        # dont print WARN
        self.spark.sparkContext.setLogLevel("ERROR")

    def get_fs(self):
        # get hadoop file system
        return self.spark._jvm.org.apache.hadoop.fs.FileSystem.get(self.spark._jsc.hadoopConfiguration())

    def check_is_file(self, hdfs_path):
        fs = self.get_fs()
        return fs.exists(self.spark._jvm.org.apache.hadoop.fs.Path(hdfs_path))

    def _to_java_object_rdd(self, rdd):
        from pyspark.serializers import PickleSerializer, AutoBatchedSerializer
        """ Return a JavaRDD of Object by unpickling
        It will convert each Python object into Java object by Pyrolite, whenever the
        RDD is serialized in batch or not.
        """
        rdd = rdd._reserialize(AutoBatchedSerializer(PickleSerializer()))
        JavaObj = rdd.ctx._jvm.org.apache.spark.mllib.api.python.SerDe.pythonToJava(rdd._jrdd, True)

        return JavaObj

    def convert_size(self, size_bytes):
        '''
        return at MB
        '''
        return size_bytes / 1024 / 1024

    def num_repartition(self, sparkDF):
        '''
        Number Partition
        If file < 128MB ==> num_partition = 1
        If file between 128MB and 256MB ==> num_partition = 2
        '''
        memory_byte = self.spark._jvm.org.apache.spark.util.SizeEstimator.estimate(
            self._to_java_object_rdd(sparkDF.rdd))
        memory_mb = self.convert_size(memory_byte)

        return int(memory_mb // (128 * 300) + 1)

    def check_keys_path_format(self, keys_path):
        import re
        if re.search('json$', keys_path):
            return True
        else:
            raise Exception("keys_path must end with '.json'")

    def autogenerate_key(self, length_key=22):
        import string
        import random

        key = ''.join(
            random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(length_key))
        key = key + "=="
        return key

    def append_keys_to_file(self, table_name, column_name=[], keys_path='keys.json'):
        from datetime import datetime
        import json

        if self.check_is_file(keys_path):
            list_keys = PyArrow().read_json(keys_path)
        else:
            list_keys = []

        c = column_name
        keys = {}

        keys["name"] = f"secret_for_{table_name}_{c}"
        keys["description"] = ""
        keys["created"] = round(datetime.timestamp(datetime.now()))
        keys["material"] = self.autogenerate_key()
        list_keys.append(keys)

        with hdfs.open_output_stream(keys_path) as file:
            json.dump(list_keys, Utf8Encoder(file))

    def encrypt_column(self, sparkDF, table_name, column_names=[], keys_path=''):
        # check file keys exist
        if self.check_is_file(keys_path):
            # Opening JSON file
            list_keys = PyArrow().read_json(keys_path)
        else:
            list_keys = []

        keys_exist = {}
        for c in column_names:
            name = f"secret_for_{table_name}_{c}"
            # check if key in file
            for k in list_keys:
                if name == k["name"]:
                    keys_exist[c] = k["material"]

        for c in column_names:
            # if not found key generate new key append to keys.json
            if c not in keys_exist.keys():
                print('Append key for', c)
                self.append_keys_to_file(table_name, c, keys_path)

        list_keys = PyArrow().read_json(keys_path)
        for c in column_names:
            name = f"secret_for_{table_name}_{c}"
            for k in list_keys:
                if name == k["name"]:
                    keys_exist[c] = k["material"]

        fields = "\n                "
        comma = ",\n                "

        for s in sparkDF.schema:
            c = s.name
            if c in column_names:
                field_dev = f"""fencrypt({c}, "{keys_exist[c]}") as {c}{comma}"""
            else:
                field_dev = f"{c}{comma}"

            fields += field_dev

        fields = fields[:-len(comma)]

        sql = f"""
        SELECT 
            {fields}
        FROM {table_name}
        """

        sparkDF.createOrReplaceTempView(f"{table_name}")
        print('Start encrypt column')

        return self.spark.sql(sql)

    def read_first_file(self, database, table_name):
        '''
        Read schema hive
        '''
        return self.spark.sql(f"""SELECT * FROM {database}.{table_name} LIMIT 5""")

    def compare_data_type(self, first_sparkDF, second_sparkDF):
        """
        Function to check when write data second time
        """
        for c in second_sparkDF.schema:
            second_type = c.dataType

            if c.name not in first_sparkDF.schema.names:
                raise ValueError(f"Column {c.name} is new column, not found in the original version")

            first_type = first_sparkDF.schema[c.name].dataType

            if first_type != second_type:
                c.name
                print("ERROR First time schema")
                print(first_sparkDF.printSchema())
                print("ERROR This time schema")
                print(second_sparkDF.printSchema())

                first_sparkDF.unpersist()
                second_sparkDF.unpersist()

                raise TypeError(
                    f"Column {c.name} dataType first time store as {first_type} but second time found {second_type}")
        print('Check schema OK')
        first_sparkDF.unpersist()

    def query_yes_no(self, question, default="yes"):
        """Ask a yes/no question via raw_input() and return their answer.

        "question" is a string that is presented to the user.
        "default" is the presumed answer if the user just hits <Enter>.
                It must be "yes" (the default), "no" or None (meaning
                an answer is required of the user).

        The "answer" return value is True for "yes" or False for "no".
        """
        valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
        if default is None:
            prompt = " [y/n] "
        elif default == "yes":
            prompt = " [Y/n] "
        elif default == "no":
            prompt = " [y/N] "
        else:
            raise ValueError("invalid default answer: '%s'" % default)

        while True:
            sys.stdout.write(question + prompt)
            choice = input().lower()
            if default is not None and choice == "":
                return valid[default]
            elif choice in valid:
                return valid[choice]
            else:
                sys.stdout.write("Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")

    def create_table_and_metadata(self, database, table_name, hdfs_path, partition_by=''):
        if database and table_name:
            try:
                self.spark.catalog.createTable(database + '.' + table_name, "hdfs://" + hdfs_path)
            except:
                # AnalysisException table aready exists
                print('Cannot create table, this table already exists ==> repair data')

        elif database and not table_name:
            raise Exception("You must add parameters table_name=")

        elif not database and table_name:
            raise Exception("You must add database=")

        if partition_by:
            print('MSCK REPAIR DATA FOR PARTITION TABLE')
            self.spark.sql(f'msck REPAIR TABLE {database}.{table_name}')
            
        self.spark.sql(f"""REFRESH TABLE {database}.{table_name}""")

    def store_spark_dataframe_to_dwh(self, data, hdfs_path, repartition=False, numPartitions=None, partition_by='',
                                     partition_date='', database='', table_name='', encrypt_columns=[], keys_path=''):
        """
         Parameters
        ----------
        data: pyspark.sql.dataframe.DataFrame
        hdfs_path : Path hdfs user want to store. EX: /data/fpt/ftel/cads/opt_customer/dm/
        partition_by: columns user want to partition, if None do not partition
        database : If user want to store to database must have database
        table_name: If user want to map data hdfs to table must have table_name
        """
        from pyspark.sql.functions import to_date, lit
        import re

        sparkDF = data
        if encrypt_columns:
            if keys_path:
                if self.check_keys_path_format(keys_path):
                    sparkDF = self.encrypt_column(sparkDF=sparkDF, table_name=table_name, column_names=encrypt_columns,
                                                  keys_path=keys_path)
            else:
                raise Exception("You must add parameters keys_path=")

        if partition_by:
            if partition_by in data.columns:
                sparkDF = sparkDF.withColumn(partition_by, to_date(partition_by))
            else:
                if not partition_date:
                    self.query_yes_no("""You should config partition_date, default today \nContinues Y/n?""")
                    from datetime import date
                    import datetime

                    today = date.today()
                    today = today.strftime("%Y-%m-%d")
                    partition_date = today

                # add constant column string ELT_DATE
                sparkDF = sparkDF.withColumn(partition_by, lit(partition_date))
                # convert string to date
                sparkDF = sparkDF.withColumn(partition_by, to_date(partition_by))

            print('HDFS path: ', hdfs_path)

            # if table exist compare datatype before store
            if self.check_is_file(hdfs_path):
                self.compare_data_type(self.read_first_file(database, table_name), sparkDF)

            self.spark.sql("SET spark.sql.sources.partitionOverwriteMode = dynamic")

            if repartition and numPartitions:
                sparkDF.repartition(numPartitions).write.mode("overwrite").partitionBy(partition_by).option("path",
                                                                                                            hdfs_path).saveAsTable(
                    database + '.' + table_name)
            elif repartition:
                numPartitions = self.num_repartition(sparkDF)
                sparkDF.repartition(numPartitions).write.mode("overwrite").partitionBy(partition_by).option("path",
                                                                                                            hdfs_path).saveAsTable(
                    database + '.' + table_name)
            else:
                sparkDF.write.mode("overwrite").partitionBy(partition_by).option("path", hdfs_path).saveAsTable(
                    database + '.' + table_name)

        else:
            sparkDF.write.mode("overwrite").option("path", hdfs_path).saveAsTable(database + '.' + table_name)
        
        self.spark.sql(f"""REFRESH TABLE {database}.{table_name}""")
        

    def to_dwh_spark(self, data, hdfs_path, repartition=False, numPartitions=None, partition_by='', partition_date='',
                     database='', table_name='', encrypt_columns=[], keys_path=''):
        """
        Parameters
        ----------
        data: pandas dataframe
        hdfs_path : Path hdfs user want to store. EX: /data/fpt/ftel/cads/opt_customer/dm/
        partition_by: columns user want to partition, if None do not partition
        database : If user want to store to database must have database
        table_name: If user want to map data hdfs to table must have table_name
        """
        # =====================================================
        sparkDF = self.spark.createDataFrame(data)
        self.store_spark_dataframe_to_dwh(sparkDF, hdfs_path=hdfs_path, repartition=repartition,
                                          numPartitions=numPartitions, partition_by=partition_by,
                                          partition_date=partition_date, database=database, table_name=table_name,
                                          encrypt_columns=encrypt_columns, keys_path=keys_path)

        
    def read_csv(self, path, sep=',', header=True):
        return self.spark.read.option("header",header).options(delimiter=sep).csv(path)
        
    def read_parquet(self, path):
        return self.spark.read.parquet(path)
    
    def describe_table(self, full_table_name, to_pandas=False):
        if to_pandas:
            pd.set_option('max_colwidth', 300)
            return self.spark.sql(f"""DESCRIBE FORMATTED {full_table_name}""").toPandas()
        else:
            return self.spark.sql(f"""DESCRIBE FORMATTED {full_table_name}""").show(100, 200)
        
        
    def show_table(self, database, to_pandas=False):
        if to_pandas:
            pd.set_option('max_colwidth', 300)
            return self.spark.sql(f"""SHOW TABLES FROM {database}""").toPandas()
        else:
            return self.spark.sql(f"""SHOW TABLES FROM {database}""").show(100, 200)
        
        
    
    
    def stop(self):
        self.spark.stop()
        return True


class PyArrow:
    def __init__(self, existing_data_behavior='overwrite_or_ignore'):
        self.existing_data_behavior = existing_data_behavior
        
    def check_keys_path_format(self, keys_path):
        import re
        if re.search('json$', keys_path):
            return True
        else:
            raise Exception("keys_path must end with '.json'")

    def autogenerate_key(self, length_key=22):
        import string
        import random

        key = ''.join(
            random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(length_key))
        key = key + "=="
        return key

    
    def read_json(self, path):
        with hdfs.open_input_file(path) as file:
            return json.load(file)
        
    def write_json(self, data, path):
        with hdfs.open_output_stream(path) as file:
            json.dump(data, Utf8Encoder(file))
    
    def append_keys_to_file(self, table_name, column_name='', keys_path='keys.json'):
        from datetime import datetime
        import json

        if self.check_is_file(keys_path):
            list_keys = self.read_json(keys_path)
        else:
            list_keys = []

        c = column_name
        keys = {}

        keys["name"] = f"secret_for_{table_name}_{c}"
        keys["description"] = ""
        keys["created"] = round(datetime.timestamp(datetime.now()))
        keys["material"] = self.autogenerate_key()
        list_keys.append(keys)

        with hdfs.open_output_stream(keys_path) as file:
            json.dump(list_keys, Utf8Encoder(file))
        
    def encrypt_column(self, data, table_name, column_names=[], keys_path=''):
        # check file keys exist
        if self.check_is_file(keys_path):
            # Opening JSON file
            list_keys = self.read_json(keys_path)
        else:
            list_keys = []

        keys_exist = {}
        for c in column_names:
            name = f"secret_for_{table_name}_{c}"
            # check if key in file
            for k in list_keys:
                if name == k["name"]:
                    keys_exist[c] = k["material"]

        for c in column_names:
            # if not found key generate new key append to keys.json
            if c not in keys_exist.keys():
                print('Append key for', c)
                self.append_keys_to_file(table_name, c, keys_path)

        list_keys = self.read_json(keys_path)
        for c in column_names:
            name = f"secret_for_{table_name}_{c}"
            for k in list_keys:
                if name == k["name"]:
                    keys_exist[c] = k["material"]
                   
        from .pandas_decrypt import encrypt_column
        for c in column_names:
            data[c] = data[c].encrypt_column(keys_exist[c])
        
        return data
    
    
    def pandas_to_parquet(self, pandas_type):
        TYPE_MAPPER = {
            'object': 'STRING',
            'float64': 'DOUBLE',
            'float32': 'DOUBLE',
            'int64': 'INT64',
            'int32': 'INT32',
            'bool': 'BOOLEAN',
            'datetime64': 'timestamp[s]',
            'datetime64[ns]': 'timestamp[s]',
            'datetime64[ns, Asia/Jakarta]': 'timestamp[s]',
            'datetime64[ns, UTC]': 'timestamp[s]'
        }

        return TYPE_MAPPER.get(pandas_type, 'None')

    def _check_series_convert_column_pyarrow(self, data, partition_by):
        
        new_type = {}
        
        # check column duplicated
        if contains_duplicates(data.columns):
            print("Columns is duplicated, check your data ")
        
        for c in data.columns:
            if str(data[c].dtype) == 'category':
                if max(data[c].str.len()) ==  min(data[c].str.len()):
                    data[c] = pd.to_datetime(data[c])
            if c == partition_by:
                new_type[partition_by] = pa.date64()
            else:

                data[c] = _check_series_convert_timestamps_internal(data[c], timezone=None)
                new_type[c] = self.pandas_to_parquet(str(data[c].dtype))

        fields = [pa.field(x, y) for x, y in new_type.items()]
        new_schema = pa.schema(fields)
        table = pa.Table.from_pandas(
            data,
            schema=new_schema,
            preserve_index=False
        )

        return table

    def check_is_file(self, hdfs_path):
        check = fs.HadoopFileSystem("hdfs://hdfs-cluster.datalake.bigdata.local").get_file_info(hdfs_path)
        if check.type._name_ in ["Directory", "File"]:
            return True
        else:
            return False

    def read_first_file(self, hdfs_path):
        '''
        Read schema pyarrow
        '''
        first_hdfs = pa.HadoopFileSystem().ls(hdfs_path)[-1]
        
        return pq.read_table(first_hdfs, filesystem=hdfs)

    def compare_data_type(self, first_sparkDF, second_sparkDF, partition_by):
        """
        Function to check when write data second time
        """
        first_sparkDF_schema = {}

        for c in first_sparkDF.schema:
            first_sparkDF_schema[c.name] = c.type

        for c in second_sparkDF.schema:
            if partition_by:
                continue

            second_type = c.type

            if c.name not in first_sparkDF.schema.names:
                raise ValueError(f"Column {c.name} is new column, not found in the original version")

            first_type = first_sparkDF_schema[c.name]

            if first_type != second_type:
                c.name
                print("ERROR First time schema")
                print(first_sparkDF.schema)
                print("ERROR This time schema")
                print(second_sparkDF.schema)

                del first_sparkDF
                del second_sparkDF

                raise TypeError(
                    f"Column {c.name} dataType first time store as {first_type} but second time found {second_type}")
        print('Check schema OK')
        del first_sparkDF

        
    def to_dwh_pyarrow(self, data, hdfs_path, database, table_name, partition_by='', partition_date='',
                       use_deprecated_int96_timestamps=True, existing_data_behavior='overwrite_or_ignore',encrypt_columns=[], keys_path=''):
        
        if encrypt_columns:
            if keys_path:
                if self.check_keys_path_format(keys_path):
                    data = self.encrypt_column(data=data, table_name=table_name, column_names=encrypt_columns, keys_path=keys_path)
            else:
                raise Exception("You must add parameters keys_path=")
                
                
        if partition_by:
            if partition_by in data.columns:
                table = self._check_series_convert_column_pyarrow(data, partition_by)
            else:
                if not partition_date:
                    from datetime import date
                    import datetime

                    today = date.today()
                    today = today.strftime("%Y-%m-%d")
                    partition_date = today

                data[partition_by] = pd.to_datetime(partition_date)
                table = self._check_series_convert_column_pyarrow(data, partition_by)

            print('HDFS path: ', hdfs_path)

            if self.check_is_file(hdfs_path):
                self.compare_data_type(self.read_first_file(hdfs_path), table, partition_by)

            pq.write_to_dataset(
                table,
                root_path=hdfs_path,
                partition_cols=[partition_by],
                use_deprecated_int96_timestamps=use_deprecated_int96_timestamps,
                filesystem=hdfs,
                existing_data_behavior=existing_data_behavior
            )

        else:
            table = self._check_series_convert_column_pyarrow(data, partition_by='')
            pq.write_to_dataset(
                table,
                root_path=hdfs_path,
                use_deprecated_int96_timestamps=use_deprecated_int96_timestamps,
                filesystem=hdfs,
                existing_data_behavior=existing_data_behavior
            )

        PySpark(driver_memory='1g', num_executors='1', executor_memory='1G').create_table_and_metadata(
            database=database, table_name=table_name, partition_by=partition_by, hdfs_path=hdfs_path)
        
        PySpark(driver_memory='1g', num_executors='1', executor_memory='1G').spark.sql(f"""REFRESH TABLE {database}.{table_name}""")


        
        
######################
def to_dwh(self, hdfs_path, database, table_name, repartition=False, numPartitions=None, partition_by='',
           partition_date='', encrypt_columns=[], keys_path='',
           driver_memory='8G', executor_memory='5g', num_executors='1', parallel=True, port='', yarn=False,
           engine='pyarrow',
           use_deprecated_int96_timestamps=True, existing_data_behavior='overwrite_or_ignore'):
    df_memory = self.memory_usage(index=True).sum() / 1024 / 1024


    if engine == 'pyarrow':
        PyArrow().to_dwh_pyarrow(data=self, hdfs_path=hdfs_path, database=database, table_name=table_name,
                                 partition_by=partition_by, partition_date=partition_date,
                                 use_deprecated_int96_timestamps=True, existing_data_behavior=existing_data_behavior, encrypt_columns=encrypt_columns, keys_path=keys_path)

    else:
        if parallel:
            num_executors = choose_num_core(df_memory)

        driver_memory = choose_driver_memory(df_memory)
        executor_memory = choose_executor_memory(df_memory, int(num_executors))

        PySpark(driver_memory=driver_memory, executor_memory=executor_memory, num_executors=num_executors, port=port,
                yarn=yarn).to_dwh_spark(data=self, hdfs_path=hdfs_path, repartition=repartition,
                                        numPartitions=numPartitions, partition_by=partition_by,
                                        partition_date=partition_date, database=database, table_name=table_name,
                                        encrypt_columns=encrypt_columns, keys_path=keys_path)


def read_table(full_table_name, engine='spark',
              driver_memory='8G', num_executors='4', executor_memory='4G', parallel=True, port='', yarn=False):
    PS = PySpark(driver_memory=driver_memory, executor_memory=executor_memory, num_executors=num_executors, port=port, yarn=yarn)
    return PS.spark.sql(f"select * from {full_table_name}")


def drop_table(full_table_name, engine='spark', yarn=False):
    PS = PySpark(driver_memory='1G', num_executors='1', executor_memory='1G', yarn=yarn)
    PS.spark.sql(f"""ALTER TABLE {full_table_name} SET TBLPROPERTIES('external.table.purge' = 'false')""")
    PS.spark.sql(f"DROP TABLE {full_table_name}")


def drop_table_and_delete_data(full_table_name, yarn=False):
    PS = PySpark(driver_memory='1G', num_executors='1', executor_memory='1G', yarn=yarn)
    PS.spark.sql(f"""ALTER TABLE {full_table_name} SET TBLPROPERTIES('external.table.purge' = 'true')""")
    PS.spark.sql(f"DROP TABLE {full_table_name}")


def sql(query, driver_memory='8G', num_executors='4', executor_memory='4G', parallel=True, port='', yarn=False):
    PS = PySpark(driver_memory=driver_memory, num_executors=num_executors, executor_memory=executor_memory, port=port, yarn=yarn)
    return PS.spark.sql(query)

def refresh_table(full_table_name, driver_memory='8G', num_executors='4', executor_memory='4G', parallel=True, port='', yarn=False):
    PS = PySpark(driver_memory=driver_memory, num_executors=num_executors, executor_memory=executor_memory, port=port, yarn=yarn)
    return PS.spark.sql(f"""REFRESH TABLE {full_table_name}""")


def read_dwh(full_table_name, filters='', engine='pyarrow', driver_memory='8G', num_executors='4', executor_memory='4G', port='', yarn=False):
    if engine == 'pyarrow':
        if filters:
            
            df_arrow = pq.read_table(source=get_location_from_table(full_table_name), filters=render_filters_pyarrow(filters), filesystem=hdfs)
            df = df_arrow.to_pandas()
        else:
            df_arrow = pq.read_table(source=get_location_from_table(full_table_name), filesystem=hdfs)
            df = df_arrow.to_pandas()
            
    if engine == 'spark':
        PS = PySpark(driver_memory=driver_memory, num_executors=num_executors, executor_memory=executor_memory, port=port, yarn=yarn)
        if filters:
            filters = 'where ' + filters
        df_spark = PS.spark.sql(f"select * from {full_table_name} {filters}")
        df = df_spark.toPandas()
    return df


def get_location_from_table(full_table_name):
    HIVE = HiveMetastoreClient(hmss_ro_addrs=["master01-dc9c14u40.bigdata.local:9083","master02-dc9c14u41.bigdata.local:9083"])
    d, t = full_table_name.split('.')

    location = HIVE.get_table(db_name=d, tb_name=t).__dict__['sd'].__dict__['location']
    import re

    pattern = re.compile('/data/')
    x = pattern.search(location)

    location = location[x.start():]
    return location


def render_filters_pyarrow(sql):
    import sqlglot
    sql = sqlglot.transpile(sql, write='spark', identify=True, pretty=True)[0]
    list_bool_expression = sql.split('\n')


    import re

    pattern_column = re.compile('`(.*?)`')
    pattern_operator = re.compile('[<>=]')


    list_filters = []
    for b in list_bool_expression:
        x1 = pattern_column.search(b)
        column_name = b[x1.start()+1: x1.end()-1]

        x2 = pattern_operator.search(b)
        operator = b[x2.start(): x2.end()]

        value = b[x2.end()+2: -1]

        list_filters.append((column_name, operator, value))
    
    return list_filters


def spark_dataframe_to_dwh(self, hdfs_path, database, table_name, repartition=False, numPartitions=None, partition_by='',
           partition_date='', encrypt_columns=[], keys_path='',
           driver_memory='8G', executor_memory='5g', num_executors='1', parallel=True, port='', yarn=False
           ):

    PySpark(driver_memory=driver_memory, executor_memory=executor_memory, num_executors=num_executors, port=port,
            yarn=yarn).store_spark_dataframe_to_dwh(data=self, hdfs_path=hdfs_path, database=database, table_name=table_name, repartition=repartition, numPartitions=numPartitions, partition_by=partition_by, partition_date=partition_date, encrypt_columns=encrypt_columns, keys_path=keys_path)
    
    
    
def read_csv(path, sep=',', header=True,
           driver_memory='8G', num_executors='4', executor_memory='4G', parallel=True, port='', yarn=False,
           engine='spark',
           use_deprecated_int96_timestamps=True, existing_data_behavior='overwrite_or_ignore'):
    PS = PySpark(driver_memory=driver_memory, num_executors=num_executors, executor_memory=executor_memory, port=port, yarn=yarn)
    return PS.read_csv(path=path, sep=sep, header=header)


def read_parquet(path,
           driver_memory='8G', num_executors='4', executor_memory='4G', parallel=True, port='', yarn=False,
           engine='spark',
           use_deprecated_int96_timestamps=True, existing_data_behavior='overwrite_or_ignore'):
    PS = PySpark(driver_memory=driver_memory, num_executors=num_executors, executor_memory=executor_memory, port=port, yarn=yarn)
    return PS.read_parquet(path=path)


def read_json(path,
           driver_memory='8G', num_executors='4', executor_memory='4G', parallel=True, port='', yarn=False,
           engine='pyarrow',
           use_deprecated_int96_timestamps=True, existing_data_behavior='overwrite_or_ignore'):
    return PyArrow().read_json(path)

def write_json(data, path,
           driver_memory='8G', num_executors='4', executor_memory='4G', parallel=True, port='', yarn=False,
           engine='pyarrow',
           use_deprecated_int96_timestamps=True, existing_data_behavior='overwrite_or_ignore'):
    return PyArrow().write_json(data = data, path = path)


###############
def ls(path):
    return pa.HadoopFileSystem().ls(path)


def mkdir(path):
    return pa.HadoopFileSystem().mkdir(path)


def cat(path):
    return pa.HadoopFileSystem().cat(path)


def exists(path):
    return pa.HadoopFileSystem().exists(path)    


def info(path):
    return pa.HadoopFileSystem().info(path) 


def open(path, mode='rb'):
    return pa.HadoopFileSystem().open(path, mode=mode)
#     if mode == 'rb':
#         return pa.HadoopFileSystem().open(path, mode=mode)
#     else:
#         print('Write wb')
#         def write(self, data):
#             print("DEBUG using Utf8Encoder")
#             if not isinstance(data, bytes):
#                 print("DEBUG using not isinstance")
#                 data = data.encode('utf-8')
#             self.fp.write(data)
        
#         from pyarrow.hdfs.HadoopFileSystem import open as o
#         o.write = write
#         return pa.HadoopFileSystem().open(path, mode=mode)

def show(self, n: int = 20, truncate: Union[bool, int] = 50, vertical: bool = False) -> None:
    """Prints the first ``n`` rows to the console.
    .. versionadded:: 1.3.0
    Parameters
    ----------
    n : int, optional
        Number of rows to show.
    truncate : bool or int, optional
        If set to ``True``, truncate strings longer than 20 chars by default.
        If set to a number greater than one, truncates long strings to length ``truncate``
        and align cells right.
    vertical : bool, optional
        If set to ``True``, print output rows vertically (one line
        per column value).
    Examples
    --------
    >>> df
    DataFrame[age: int, name: string]
    >>> df.show()
    +---+-----+
    |age| name|
    +---+-----+
    |  2|Alice|
    |  5|  Bob|
    +---+-----+
    >>> df.show(truncate=3)
    +---+----+
    |age|name|
    +---+----+
    |  2| Ali|
    |  5| Bob|
    +---+----+
    >>> df.show(vertical=True)
    -RECORD 0-----
     age  | 2
     name | Alice
    -RECORD 1-----
     age  | 5
     name | Bob
    """

    if not isinstance(n, int) or isinstance(n, bool):
        raise TypeError("Parameter 'n' (number of rows) must be an int")

    if not isinstance(vertical, bool):
        raise TypeError("Parameter 'vertical' must be a bool")

    if isinstance(truncate, bool) and truncate:
        print(self._jdf.showString(n, 20, vertical))
    else:
        try:
            int_truncate = int(truncate)
        except ValueError:
            raise TypeError(
                "Parameter 'truncate={}' should be either bool or int.".format(truncate)
            )

        print(self._jdf.showString(n, int_truncate, vertical))
        
### new function
def info(self, driver_memory='8G', num_executors='4', executor_memory='4G', parallel=True, port='', yarn=False):
    sdf = self
    sdf.createOrReplaceTempView('info_table')
    sql = ''
    
    for c in sdf.schema.names[:-1]:
        check_column = f"""
            SELECT '{c}' column,
            count(case when {c} is null or {c} is not null then 1 end) total_count, 
            count(case when {c} is null then 1 end) is_null_count,
            ROUND(count(case when {c} is null then 1 end) / count(case when {c} is not null or {c} is null then 1 end), 4) percent_isnull FROM info_table \n"""
        sql += check_column
        sql += 'UNION ALL \n'

    check_column_end = f"""
            SELECT '{c}' column,
            count(case when {c} is null or {c} is not null then 1 end) total_count, 
            count(case when {c} is null then 1 end) is_null_count,
            ROUND(count(case when {c} is null then 1 end) / count(case when {c} is not null or {c} is null then 1 end), 4) percent_isnull FROM info_table \n"""
    sql += check_column_end.format(c=sdf.schema.names[-1])
    PS = PySpark(driver_memory=driver_memory, num_executors=num_executors, executor_memory=executor_memory, port=port, yarn=yarn)
    return PS.spark.sql(sql)