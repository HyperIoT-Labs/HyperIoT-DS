import sys
import json
from pyspark.sql import SparkSession
from pyspark.sql import DataFrame
from pyspark.sql.functions import *
from functools import reduce
import happybase

# Creazione Sessione Spark
spark = SparkSession.builder\
    .appName('HYOT_Neural_Network_train') \
    .config("spark.hadoop.dfs.client.use.datanode.hostname", "true") \
    .enableHiveSupport() \
    .getOrCreate()

# Project ID
projectId = sys.argv[1]

# Algorithm ID
algorithmId = sys.argv[2]

# HProjectAlgorithm name
hProjectAlgorithmName = sys.argv[3]

# Hadoop & HBase job config
configs = sys.argv[4].replace('\\"', '"')
oldJobConfig = json.loads(configs)

# HADOOP
hbaseRootdir = oldJobConfig['hbaseRootdir']
hdfsWriteDir = oldJobConfig['hdfsWriteDir']
hbaseURL = hbaseRootdir.replace("/hbase", "") + hdfsWriteDir

# HBASE
hbaseMaster = oldJobConfig['hbaseMaster'].replace(":16000", "")

# INPUT/OUTPUT JOB CONFIG
inputs = sys.argv[5].replace('\\"', '"')
jobConfig = json.loads(inputs)

# Retrieve information from argument JSONs
hPacketId  = jobConfig['input'][0]['packetId']
hPacketFieldId = jobConfig['input'][0]['mappedInputList'][0]['packetFieldId']
hPacketFieldType = jobConfig['input'][0]['mappedInputList'][0]['algorithmInput']['fieldType']
hPacketFieldType = "double" if hPacketFieldType == "NUMBER" else hPacketFieldType

# Same name of script
outputName = hProjectAlgorithmName

# HDFS path
path_file = f"{hbaseURL}{hPacketId}/20*"

# Create merged dataset
df_list =[]
temp = spark.read.format("avro").load(path_file)
temp = temp.select(explode(map_values(temp.fields)).alias("hPacketField")).filter(col("hPacketField.id") == hPacketFieldId)
df_list.append(temp)
df_complete = reduce(DataFrame.union, df_list)
df_complete = df_complete.orderBy(rand())

# Explode column FIELDS
value = df_complete.select(
    ("hPacketField.value.member0"),
    ("hPacketField.value.member1"),
    ("hPacketField.value.member2"),
    ("hPacketField.value.member3"),
    ("hPacketField.value.member4"),
    ("hPacketField.value.member5"),
    ("hPacketField.value.member6")) 

# MAX (CHANGE STATISTIC TYPE HERE)
output = value.select(coalesce(value.member0.cast("string"), value.member1.cast("string"),
                               value.member2.cast("string"), value.member3.cast("string"),
                               value.member4.cast("string"), value.member5.cast("string"),
                               value.member6.cast("string")).alias('value')).select(col("value").cast("double")).select(max(col("value")))

# Write into HBase
connection = happybase.Connection(host=hbaseMaster, port=9090, protocol="binary")

connection.open()
table_name = "algorithm" + "_" + algorithmId + "_"

try:
    connection.create_table(table_name, {'value': dict()})
except:
    print("TABLE ALREADY EXISTS!")
    
HbaseTable = connection.table(table_name)

for row in output.collect():
    keyValue = projectId + "_" + hProjectAlgorithmName + "_" + ''
    columnFamily = 'value'
    val = str(row[0])
    column = outputName

    HbaseTable.put(keyValue.encode("utf-8"), {columnFamily.encode("utf-8") +":".encode("utf-8")+ column.encode("utf-8"): val.encode("utf-8")})

# Close all connections
connection.close()
spark.stop()
