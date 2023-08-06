"""
Owner: kuldeep.singh@zeno.health
Purpose: This script calculates the drug substitutes. Which means, what all drug ids can be
substituted by each other.
And lastly, it is stored in a table.
"""
import argparse
import sys
import os

sys.path.append('../../../..')

from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.db.db import DB, MySQL

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False,
                    help="This is env(dev, stage, prod)")
parser.add_argument('-mtp', '--main_table_prefix', default="-main", type=str, required=False)
parser.add_argument('-ttp', '--temp_table_prefix', default="-temp", type=str, required=False)

args, unknown = parser.parse_known_args()
env = args.env
main_table_prefix = args.main_table_prefix
temp_table_prefix = args.temp_table_prefix
main_table_prefix = "" if main_table_prefix == "NA" else main_table_prefix

os.environ['env'] = env
logger = get_logger()

""" read connection """
db = DB()
db.open_connection()

mysql_write_db = MySQL(read_only=False)
mysql_write_db.open_connection()

table_name = "drug-substitution-mapping"
ms_write_schema = "test-generico" if env in ("dev", "stage") else "prod2-generico"
temp_table_name = f"`{ms_write_schema}`.`{table_name}{temp_table_prefix}`"
main_table_name = f"`{ms_write_schema}`.`{table_name}{main_table_prefix}`"


def get_drug_groups():
    query = f"""
    select
        dm."drug-id",
        listagg(DISTINCT dm."molecule-group-or-name" || dm."unit-type-value" || dm."unit-type" || "release-pattern-group" || "available-in-dose-form-group") within group (
    order by
        dm."molecule-group-or-name") as "combination",
        md5(listagg(DISTINCT dm."molecule-group-or-name" || dm."unit-type-value" || dm."unit-type" || "release-pattern-group" || "available-in-dose-form-group") within group (
        order by dm."molecule-group-or-name")) as "group"
    from
        (
        select
            d.id as "drug-id",
            case
                when (mm."molecule-group" = ''
                or mm."molecule-group" is null) then mm.name
                else mm."molecule-group"
            end as "molecule-group-or-name",
            cmmmm."unit-type-value",
            cmmmm."unit-type",
            rpm."group" as "release-pattern-group",
            aidfm."available-group" as "available-in-dose-form-group"
        from
            "prod2-generico".drugs d
        inner join "prod2-generico"."composition-master" cm on
            d."composition-master-id" = cm.id
        inner join "prod2-generico"."composition-master-molecules-master-mapping" cmmmm on
            cm.id = cmmmm."composition-master-id"
        inner join "prod2-generico"."molecule-master" mm on
            mm.id = cmmmm."molecule-master-id"
        inner join "prod2-generico"."drug-molecule-release" dmr on
            d.id = dmr."drug-id"
            and cmmmm."molecule-master-id" = dmr."molecule-master-id"
        inner join "prod2-generico"."available-in-dosage-form-mapping" aidfm on
            d."available-in" = aidfm."available-in"
            and d."dosage-form" = aidfm."dosage-form"
        inner join "prod2-generico"."prod2-generico"."release-pattern-master" rpm on
            dmr."release" = rpm.name
            --	where
            --		d.id = 494855
        order by
            1,
            2) dm
    group by
        dm."drug-id"
    """
    return db.get_df(query=query)


drug_group_df = get_drug_groups()
total_count = len(drug_group_df)
logger.info(f"Total drug count: {total_count}")

# Truncate the temp table before starting
query = f""" truncate table  {temp_table_name};"""
mysql_write_db.engine.execute(query)

# store the data in the temp table
drug_group_df.to_sql(
    con=mysql_write_db.engine, name=f"{table_name}{temp_table_prefix}", schema=ms_write_schema,
    if_exists="replace", chunksize=500)

# Delete the data from temp table which is already present in main table
query = f""" DELETE FROM t1 USING {temp_table_name} t1 INNER JOIN {main_table_name} t2 ON
        ( t1.`drug-id` = t2.`drug-id` and t1.group = t2.group); """

response = mysql_write_db.engine.execute(query)
present_correct_count = response.rowcount
logger.info(f"Correct drug-ids count: {present_correct_count}")

# Delete the incorrect substitutes from main table
query = f""" DELETE FROM t1 USING {main_table_name} t1 INNER JOIN {temp_table_name} t2 ON
        ( t1.`drug-id` = t2.`drug-id` );"""

response = mysql_write_db.engine.execute(query)
present_incorrect_count = response.rowcount
logger.info(f"Incorrect drug-ids count: {present_incorrect_count}")

# Now Insert the records in main table
query = f""" INSERT INTO {main_table_name} (`drug-id`, `combination`, `group`)
        SELECT `drug-id`, `combination`, `group` FROM {temp_table_name} """
response = mysql_write_db.engine.execute(query)
new_insert_count = response.rowcount
logger.info(f"Insert/Update drug-ids count: {new_insert_count}")

if total_count == present_correct_count + new_insert_count:
    logger.info("Drug substitute data updated successfully")
else:
    raise Exception("Data count mismatch")
