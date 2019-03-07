from . import var
from . import utility as utl
from . import process as prc
import sqlite3 as sql
import os, time, datetime


def read_database_lines(table):
    """
    Returns all the lines in the table from the database at the beginning for the MemesAnalyser initialisation

    :param table: the name of the table
    :type table: str
    :return:
    """
    connection = sql.connect(var.DATABASE_PATH)
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM {table}")
    data = cursor.fetchall()
    cursor.close()
    connection.close()
    return data


class Databaser(prc.Process):
    """
    Class of the Databaser process
    """

    def __init__(self, *args, **kwargs):
        """
        Initialises a new Databaser object and connects to the database

        :param args:
        :param kwargs:
        """
        super(Databaser, self).__init__(*args, **kwargs)
        try:
            os.mkdir(var.TMP_DIR)
        except FileExistsError:
            pass
        utl.copy_file(var.DATABASE_PATH, var.TMP_DATABASE_PATH)
        self.last_backup = time.time()
        self.connection = sql.connect(var.TMP_DATABASE_PATH)
        self.cursor = self.connection.cursor()
        self._create_tables()
        self.last_time = 0
        self.count = 0

    def _create_tables(self):
        """
        Creates the database tables if they don't exist

        :return:
        """
        for table in var.DATABASE_TABLES:
            columns = ""
            for i in var.DATABASE_TABLES[table]:
                columns += "" + i + " " + var.DATABASE_TABLES[table][i] + ","
            self.cursor.execute(f"CREATE TABLE IF NOT EXISTS '{table}' ({columns[:-1]})")

    def _run(self):
        """
        Method called by the run() method at process start
        Gets analysed memes from the database pipe and saves them to the database
        Backups the database regularly over time

        :return:
        """
        meme = None
        while True:
            try:
                meme = self.pipe_get('database')
                self.save(meme)
                self.connection.commit()
                if time.time() > self.last_backup + var.TIME_BETWEEN_BACKUPS:
                    self.backup()
            except StopIteration:
                raise
            except Exception as e:
                if meme:
                    add = {'source_ID': meme.source_ID, 'ID': meme.ID, 'template_ID': meme.template_ID, 'match': meme.match, 'score': meme.score, 'time': meme.time}
                else:
                    add = None
                self.track_error(to_file=True, error=e, additional=add)

    def save(self, meme):
        """
        Adds the given meme's data to the database

        :param meme:
        :return:
        """
        self.cursor.execute(f"INSERT INTO matches VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (
            meme.source_ID, meme.ID, meme.template_ID, utl.get_int(meme.part_match[0][0]), meme.part_match[0][2], meme.part_match[0][1][0], meme.part_match[0][1][1],
            utl.get_int(meme.part_match[1][0]),
            meme.part_match[1][2], meme.part_match[1][1][0], meme.part_match[1][1][1], utl.get_int(meme.part_match[2][0]), meme.part_match[2][2], meme.part_match[2][1][0], meme.part_match[2][1][1],
            utl.get_int(meme.match), meme.score, meme.time))
        self.cursor.execute(f"UPDATE templates SET counts = counts + 1 WHERE ID = ?", (meme.template_ID,))
        self.cursor.execute(f"UPDATE sources SET counts = counts + 1 , last_time = MAX(last_time, ?) WHERE ID = ?", (meme.time, meme.source_ID))
        self.last_time = meme.time
        self.count += 1

    def backup(self):
        """
        Copies the database from the temporary directory to the project directory

        :return:
        """
        self.terminal.info("Database backup started...")
        utl.copy_file(var.TMP_DATABASE_PATH, var.DATABASE_PATH)
        self.last_backup = time.time()
        self.terminal.ok(
            f"{utl.get_time()}: Backup completed - {self.count} entries written, {self.count / var.TIME_BETWEEN_BACKUPS} per second. We are around {datetime.datetime.fromtimestamp(self.last_time).strftime(var.TIME_STAMP)}")
        self.count = 0

    def exit(self):
        """
        Exits the process closing the database connections and making a final backup

        :return:
        """
        self.connection.commit()
        self.cursor.close()
        self.connection.close()
        self.backup()
        super(Databaser, self).exit()
