from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, round, when, sum, desc
from pyspark.sql.types import StringType, IntegerType
import os
from CsvToGraph import CsvToGraph
from pyspark.context import SparkContext, SparkConf


class ReadCsv:

    def __init__(self):
        # Create SparkSession
        self.spark = (SparkSession
                      .builder
                      .appName("MonApplication")
                      # .master("yarn")
                      # .config("spark.hadoop.security.authentication", "simple")
                      # .config("spark.driver.extraJavaOptions", "-Djava.security.manager=allow")
                      .getOrCreate())

        # self.sc = SparkContext()

    def getSpark(self, filename="tp_arbre/les-arbres.csv", delimiter=';'):
        option = {
            "header": True,
            "inferSchema": True,
            "delimiter": delimiter
        }
        df = (self.spark.read.format("csv")
              .options(**option)
              .load(filename)
              )

        return df

    def readCsv(self):
        df = self.getSpark()
        df_1 = (df.select(
            col("ARRONDISSEMENT").cast(StringType()),
            col("CIRCONFERENCE (cm)").cast(IntegerType()),
            col("LIEU / ADRESSE").cast(StringType())
        )
                .filter(col("ARRONDISSEMENT").contains("PARIS"))
                .groupby("ARRONDISSEMENT")
                .agg(round(avg("CIRCONFERENCE (cm)"), 2).alias("CIRCONFERENCE MOYENNE (cm)"))
                .orderBy(col("CIRCONFERENCE MOYENNE (cm)").desc())
                )

        df_2 = (df.select(
            col("DOMANIALITE").cast(StringType()),
            col("ARRONDISSEMENT").cast(StringType()),
            col("TYPE EMPLACEMENT").cast(StringType()),
            col("LIEU / ADRESSE").cast(StringType())
        )
                .filter((col("DOMANIALITE").contains("CIMETIERE")) & (col("ARRONDISSEMENT").contains("PARIS")))
                .withColumn("TYPE EMPLACEMENT", when(col("TYPE EMPLACEMENT").contains("Arbre"), 1).otherwise(0))
                .groupby("ARRONDISSEMENT")
                .agg(sum("TYPE EMPLACEMENT").alias("TOTAL ARBRES"))
                .orderBy(col("TOTAL ARBRES").desc())
                )

        df_3 = df.select(col("LIBELLE FRANCAIS"), col("GENRE")) \
                .where((col("LIEU / ADRESSE").like("%ECOLE MATERNELLE%") |
                       col("LIEU / ADRESSE").like("%ECOLE PRIMAIRE%") |
                       col("LIEU / ADRESSE").like("%COLLEGE%") |
                       col("LIEU / ADRESSE").like("%LYCEE%")) &
                       col("ARRONDISSEMENT").like("% ARRDT")) \
                .groupby(["LIBELLE FRANCAIS", "GENRE"]) \
                .count() \
                .sort(desc("count")) \
                .limit(10)

        self.exportCsv(df_1, df_2, df_3)

    def exportCsv(self, df_1, df_2, df_3):
        try:
            output_path_1 = "tp_arbre/shared_volume/result_circonference.csv"
            df_1.write.csv(output_path_1, header=True, mode='overwrite')

            output_path_2 = "tp_arbre/shared_volume/result_cimetiere.csv"
            df_2.write.csv(output_path_2, header=True, mode="overwrite")

            output_path_3 = "tp_arbre/shared_volume/result_ecole.csv"
            df_3.write.csv(output_path_3, header=True, mode="overwrite")

            # if os.path.exists(output_path_1):
            print("Le fichier CSV1 a été écrit avec succès.")
            csvToGraph = CsvToGraph()
            csvToGraph.csvToGraph(
                output_path_1,
                "ARRONDISSEMENT",
                "CIRCONFERENCE MOYENNE (cm)",
                'Circonférence Moyenne par Arrondissement à Paris',
                'graph_circonference.png'
            )

            print("Le fichier CSV2 a été écrit avec succès.")
            csvToGraph.csvToGraph(
                output_path_2,
                "TOTAL ARBRES",
                "ARRONDISSEMENT",
                'Arrondissements qui ont le plus d’arbres par cimetière',
                'graph_cimetiere.png',
                'barh'
            )

            print("Le fichier CSV3 a été écrit avec succès.")
            csvToGraph.csvToGraph(
                output_path_3,
                "count",
                "LIBELLE FRANCAIS",
                'Variétés d’arbres les plus présentes dans les établissements scolaires',
                'graph_ecole.png',
                'barh'
            )

            print("en cours de sauvegarde ...")
            os.system("hdfs dfs -get /user/root/tp_arbre/shared_volume/ /tp_arbre/")
            print("fin de sauvegarde.")

            # else:
            #     print("Échec de l'écriture du fichier CSV.")
        except Exception as e:
            print(f"Une erreur est survenue : {e}")
