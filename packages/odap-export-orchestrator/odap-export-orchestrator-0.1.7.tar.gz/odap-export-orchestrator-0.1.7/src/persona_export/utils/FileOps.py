import json
import logging

from pyspark.sql import SparkSession
import IPython as ip


def _get_spark() -> SparkSession:
    user_ns = ip.get_ipython().user_ns
    if "spark" in user_ns:
        return user_ns["spark"]
    else:
        spark = SparkSession.builder.getOrCreate()
        user_ns["spark"] = spark
        return spark


def _get_dbutils(spark: SparkSession):
    try:
        from pyspark.dbutils import DBUtils
        dbutils = DBUtils(spark)
    except ImportError:
        dbutils = ip.get_ipython().user_ns.get("dbutils")
        if not dbutils:
            logging.warning("could not initialise dbutils!")
    return dbutils


class FileOps:
    """ Service class for safe IO operation over files

        TODO no error handling within this version yet
    """

    OPERATION_READ = "r"
    OPERATION_WRITE = "w"
    spark: SparkSession = _get_spark()
    dbutils = _get_dbutils(spark)

    @classmethod
    def write(cls, path: str, data):
        with open(path, cls.OPERATION_WRITE) as f:
            json.dump(data, f, indent=4, sort_keys=True)

    @classmethod
    def read(cls, path: str):
        if 'dbfs' in path:
            with open(path, cls.OPERATION_READ) as f:
                return json.loads(f.read())
        else:
            cls.dbutils.fs.cp(path, f"/tmp/config/{path.split('/')[-1]}")
            with open(f"/dbfs/tmp/config/{path.split('/')[-1]}", cls.OPERATION_READ) as f:
                return json.loads(f.read())
            # file = cls.spark.read.json(path)
            # return (file.collect()[0]).asDict()

    @classmethod
    def size(cls, path):
        return cls.dbutils.fs.ls(path)[-1][-1]

    @classmethod
    def file_list(cls, path):
        files = []
        for file in cls.dbutils.fs.ls(path):
            files.append(file[1])
        return files

    @classmethod
    def remove_dbfs(cls, path):
        return cls.dbutils.fs.rm(path, True)

    @classmethod
    def copy_dbfs(cls, path, destination):
        return cls.dbutils.fs.cp(path, destination)

    @classmethod
    def run_notebook(cls, path, run_time, widgets):
        return cls.dbutils.notebook.run(path, run_time, widgets)

    @classmethod
    def read_delta_table(cls, delta_to_read):
        return cls.spark.read.format("delta").load(delta_to_read)

    @classmethod
    def create_folder(cls, folder):
        return cls.dbutils.fs.mkdirs(folder)
