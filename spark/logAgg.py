from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as _sum, lit, concat
import os
import shutil

spark = SparkSession.builder \
    .appName("Log Aggregation with Article ID") \
    .getOrCreate()


base_input_dir = "/mnt/c/Users/dell/Desktop/Chocolux Free Website Template - Free-CSS.com/nifi"  
output_dir = "/mnt/c/Users/dell/Desktop/Chocolux Free Website Template - Free-CSS.com/output"  


os.makedirs(output_dir, exist_ok=True)


hour_dirs = [os.path.join(base_input_dir, d) for d in os.listdir(base_input_dir) if os.path.isdir(os.path.join(base_input_dir, d))]

if not hour_dirs:
    print("Aucun dossier d'heures trouvé dans le répertoire 'nifi'.")
    spark.stop()
    exit()

for hour_dir in hour_dirs:
    hour = os.path.basename(hour_dir)  # Récupérer le nom du dossier (exemple : "2023051012")

    try:
        
        logs_df = spark.read.option("delimiter", "|") \
            .csv(os.path.join(hour_dir, "*.txt"), header=False)

        
        logs_df = logs_df.withColumnRenamed("_c0", "timestamp") \
                         .withColumnRenamed("_c1", "article") \
                         .withColumnRenamed("_c2", "id") \
                         .withColumnRenamed("_c3", "price") \
                         .withColumn("price", col("price").cast("long"))  # Convertir "price" en entier

        
        aggregated_df = logs_df.groupBy("article", "id") \
            .agg(_sum("price").alias("total_sales"))

        result_df = aggregated_df.withColumn("hour", lit(hour)) \
            .select(concat(
                lit(hour[:4] + "/" + hour[4:6] + "/" + hour[6:8] + " ")
            ).alias("date_id"),
                col("id"),
                col("article"),
                col("total_sales"))

       
        result_df = result_df.withColumn("output", concat(
            col("date_id"), lit(" "), col("id"), lit("|"), col("article"), lit("|"), col("total_sales")
        ))

               result_df = result_df.select("output").coalesce(1)

               temp_dir = os.path.join(output_dir, f"{hour}_temp")
        result_df.write.mode("overwrite").text(temp_dir)

               for file_name in os.listdir(temp_dir):
            if file_name.startswith("part-") and file_name.endswith(".txt"):
                shutil.move(os.path.join(temp_dir, file_name), os.path.join(output_dir, f"{hour}.txt"))

               shutil.rmtree(temp_dir)

        print(f"Fichier agrégé écrit pour l'heure {hour} : {os.path.join(output_dir, f'{hour}.txt')}")

    except Exception as e:
        print(f"Erreur lors du traitement du dossier {hour_dir} : {e}")

spark.stop()