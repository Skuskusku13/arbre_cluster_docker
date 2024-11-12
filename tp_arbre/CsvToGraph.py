import os

import matplotlib.pyplot as plt
from pyspark.sql import SparkSession
from pyspark.context import SparkContext, SparkConf
class CsvToGraph:

    def __init__(self):
        # Create SparkSession
        self.spark = (SparkSession
            .builder
            .appName("MonApplication")
            # .master("yarn")
            # .config("spark.hadoop.security.authentication", "simple")
            # .config("spark.driver.extraJavaOptions", "-Djava.security.manager=allow")
            .getOrCreate())

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

    def csvToGraph(self, pathfile, name_x, name_y, title, name_graph, graph = 'bar'):
        df = self.getSpark(pathfile, ',')
        try:
            # Extraire les colonnes et valeurs pour le graphique
            col_x = df.select(name_x).rdd.flatMap(lambda x: x).collect()
            col_y = df.select(name_y).rdd.flatMap(lambda x: x).collect()

            if col_x and col_y:
                fig, ax = plt.subplots(figsize=(12, 6))

                if graph == 'bar':
                    ax.bar(col_x, col_y, color='forestgreen') #forestgreen
                    ax.invert_xaxis()
                else :
                    # ("barh")
                    ax.barh(col_y, col_x, color='forestgreen') #forestgreen

                ax.set_ylabel(str(name_y).title())
                ax.set_xlabel(str(name_x).title())
                ax.set_title(str(title).title())
                # ax.invert_yaxis()
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()

                # Enregistrer le graphique && afficher
                # plt.savefig(f'graph/{name_graph}', format='png')
                plt.savefig(fname=f'graph/{name_graph}', format='png')
                # plt.show()
                print(f'fichier {name_graph} sauvegardé')

            else:
                print("Les données pour le graphique sont vides.")
        except Exception as e:
            print(f"Erreur lors de la création du graphique : {e}")
