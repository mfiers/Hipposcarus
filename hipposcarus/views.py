
import os
import tempfile
import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

from flask import send_from_directory
from flask import Flask, render_template, request, url_for

from werkzeug.contrib.cache import SimpleCache

import pymongo

from .util import render, get_flask_app
from . import util
from .data import get_latest_csum, get_trans_db, get_transact_dbs, get_waste_db

CACHE = SimpleCache()
app = get_flask_app()


@app.route("/")
def index():
    context = {}
    context['title'] = "Hipposcarus"
    _time, csum = get_latest_csum()
    context['nofiles'] = csum['count'].sum()
    context['nobytes'] = csum['sum'].sum()

    return render('index.html', context)

@app.route("/waste")
@app.route("/waste/")
@app.route("/waste/<text>")
def waste(text=None):

    global CACHE

    cachename = 'waste' if text is None else 'waste_text'
    rv = CACHE.get(cachename)
    if not rv is None:
        return rv

    context = {}
    context['text'] = text
    wdb = get_waste_db()
    clc = get_trans_db()

    w = list(wdb.find().sort('time', pymongo.DESCENDING).limit(1))[0]
    data = pd.DataFrame(w['data'][:20])
    csum_data = {}
    context['total_waste'] = data['waste'].sum()

    for name, row in data.iterrows():
        cd = list(clc.find({"sha1sum": row['_id']}))
        csum_data[row['_id']] = cd

    context['w'] = w
    context['csum'] = csum_data
    context['data'] = data

    rv = render('waste.html', context)
    CACHE.set(cachename, rv, timeout=12 * 60 * 60)
    return rv

@app.route("/sha1sum/")
@app.route("/sha1sum/<sha1sum>")
def sha1sum_view(sha1sum=None):


    clc = get_trans_db()
    sh2t_db, t_db = get_transact_dbs()

    context = {'sha1sum': sha1sum}
    query = {'sha1sum' : sha1sum}
    result = clc.find(query)
    context['res'] = list(result)

    #transcation#s
    tacts = [x['transaction_id'] for x in sh2t_db.find({'sha1sum': sha1sum})]
    transactions = list(t_db.find({'_id': {"$in": tacts}}))
    for t in transactions:
        t['iocats'] = set([x['category'] for x in t['io']])

    context['transactions'] = transactions


    return render('sha1sum.html', context)


@app.route("/aggregate", methods=['get', 'post'])
def aggregate_view():

    aggregate_on = request.args.get('aggon', 'category')

    time, csum = get_latest_csum()
    stime = time.strftime("%Y-%m-%y")

    context = {}
    context['time'] = time
    context['stime'] = stime
    context['aggon'] = aggregate_on
    context['title'] = "%s/%s" % (time.strftime('%Y-%m-%d'), aggregate_on)
    context['nofiles'] = csum['count'].sum()
    context['nobytes'] = csum['sum'].sum()
    context['csum'] = csum

    filters = {}
    filters_selected = {}

    original_csum = csum.copy()

    for ftype in 'pi project volume filetype backup'.split():
        selected = request.args.get('filter_' + ftype, "")
        if selected:
            selected = pd.Series(selected.split(','))
            selected[selected=='None'] = None
            selected = list(selected)
            csum = csum[csum[ftype].isin(selected)]
            filters_selected[ftype] = selected
        filters[ftype] = original_csum[ftype].copy().drop_duplicates()

    context['filters'] = filters
    context['filters_selected'] = filters_selected

    context['empty_result'] = False
    if len(csum) == 0:
        context['empty_result'] = True
        return render('simple.html', context)

    context['fileview'] = False
    if request.args.get('fileview', "") == "on":
        #return fileset
        context['fileview'] = True
        clc = get_trans_db()
        query = {}
        for sf, ss in filters_selected.items():
            query[sf] = { "$in": ss }
        results = clc.find(query).sort([("filesize", -1)]).limit(10)
        context['files'] = results
        return render('simple.html', context)




    #Aggregate & plot
    agg = csum[[aggregate_on, 'sum', 'count']]\
      .fillna('(undefined)')\
      .groupby(aggregate_on)\
      .sum()

    context['agg'] = agg

    dyndir = util.get_dynamic_dir(stime)

    if max(agg['sum']) > 1e12:
        agg['sum'] /= 1e12
        unit = 'Tb'
    elif max(agg['sum']) > 1e9:
        agg['sum'] /= 1e9
        unit = 'Gb'
    elif max(agg['sum']) > 1e6:
        agg['sum'] /= 1e6
        unit = 'Mb'
    else: unit = 'b'

    if max(agg['count']) > 1e9:
        agg['count'] /= 1e9
        cunit = 'g'
    elif max(agg['count']) > 1e6:
        agg['count'] /= 1e6
        cunit = 'm'
    if max(agg['count']) > 1e3:
        agg['count'] /= 1e3
        cunit = 'k'
    else:
        cunit = ''

    dd = agg.sort('sum', inplace=False, ascending=False).copy()
    plt.figure(figsize=(8, 6))

    if len(dd) > 20:
        rs = dd.iloc[19:,:].sum()
        dd = dd.iloc[:19,:]
        dd.loc['(rest)'] = rs

    plt.subplots_adjust(wspace=0.1)
    plt.subplot(121)
    sns.barplot(data=dd, x='sum', y=dd.index)
    plt.xlabel("")
    plt.title("Sum (%s)" % unit)
    ax2 = plt.subplot(122)
    sns.barplot(data=dd, x='count', y=dd.index)
    ax2.get_yaxis().set_visible(False)
    plt.ylabel(""); plt.xlabel("")
    if cunit:
        plt.title("Count (%s)" % cunit)
    else: plt.title("Count")

    outfile = tempfile.NamedTemporaryFile(delete=False, dir=dyndir, suffix='.agg.png')
    outfile.close()
    plt.tight_layout()
    plt.savefig(outfile.name)
    context['aggplot'] = '/dyn/%s/%s' % (stime, os.path.basename(outfile.name))

    return render('simple.html', context)


@app.route('/dyn/<path:path>')
def send_dynamic(path):
    ddir = util.get_dynamic_dir()
    return send_from_directory(ddir, path)
