import psycopg2
import config
import datetime
from aiogram import types


def chek_paper_in_db(id_user: int, paper: str):
    with psycopg2.connect(host=config.HOST, database=config.DBNAME, user=config.USER, password=config.PASSWORD) as conn:
        curr = conn.cursor()
        curr.execute("select paper from watch_list where id_user = %s and paper = '%s'"
                     % (id_user, paper))
        rec = curr.fetchall()
        return rec


def add_paper_in_db(id_user, paper):
    with psycopg2.connect(host=config.HOST, database=config.DBNAME, user=config.USER, password=config.PASSWORD) as conn:
        curr = conn.cursor()
        curr.execute("insert into watch_list (id_user, paper) values (%s, '%s')"
                     % (id_user, paper))


def del_paper_in_db(id_user, paper):
    """
    Скорректировать запрос
    :param id_user:
    :param paper:
    :return:
    """
    with psycopg2.connect(host=config.HOST, database=config.DBNAME, user=config.USER, password=config.PASSWORD) as conn:
        curr = conn.cursor()
        curr.execute("delete from watch_list where id_user = %s and paper = '%s'" % (id_user, paper))


def get_my_list(id_user: int):
    with psycopg2.connect(host=config.HOST, database=config.DBNAME, user=config.USER, password=config.PASSWORD) as conn:
        curr = conn.cursor()
        curr.execute("select paper from watch_list where id_user = %s" % id_user)
        return curr.fetchall()