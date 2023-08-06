# import os, sys
from pprint import pprint as pp
from uuid import uuid4 as u4

from declang.processor import process_language

from langutils.app.treeutils import (
    anak,
    data,
    token,
)


kode_chart = """
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style('darkgrid')
plt.rcParams["figure.autolayout"] = True
warna_untuk_piechart = sns.color_palette('pastel')[0:5]

__TEMPLATE_CODE__


"""

output = {}


def reset():
    global output
    output.clear()


def charthandler(tree, parent=""):
    namaparent = ""
    itemid = ""
    for item in anak(tree):
        jenis = data(item)
        print(jenis)
        if jenis == "element_name":
            nama = token(item)
            # print('  ', nama, f'berortu [{parent}]')
            namaparent = token(item)
            itemid = str(u4())
            if nama == "canvas":
                print("canvas")
                output["canvas"] = {}
            elif nama == "piechart":
                print("  pie")
            elif nama == "barchart":
                print("  bar")
            elif nama == "linechart":
                print("  line")
            elif nama == "donutchart":
                print("  donut")
            elif nama == "map":
                print("  map")
        elif jenis == "element_children":
            for bagian in anak(item):
                for bagianlagi in bagian:
                    # print('  ', type(bagianlagi), '=>', bagianlagi, '=>', data(bagianlagi))
                    if data(bagianlagi) == "declarative_element":
                        charthandler(bagianlagi)
        elif jenis == "element_config":
            for tupleitem in anak(item):
                jenis2 = data(tupleitem)
                if jenis2 == "item_key_value":
                    k, v = "", ""
                    for anaktupleitem in anak(tupleitem):
                        jenis3 = data(anaktupleitem)
                        if jenis3 == "item_key":
                            k = token(anaktupleitem)
                        elif jenis3 == "item_value":
                            v = token(anaktupleitem)
                    print(f"  attr {namaparent}/{itemid} k=v => {k}={v}")
                    if namaparent == "canvas":
                        pass
                    else:
                        if not itemid in output["canvas"]:
                            output["canvas"][itemid] = {
                                "type": namaparent,
                                "attrs": [f"{k}={v}"],
                            }
                        else:
                            output["canvas"][itemid]["attrs"].append(f"{k}={v}")


def process_output(output):
    templatecodes = []

    if "canvas" in output:
        for _id, kamus in output["canvas"].items():
            if kamus["type"] in ["barchart", "linechart", "piechart", "donutchart"]:
                mode = "B"
                chartname = 'chartname = "bar1.png"'
                chartfunction = "sns.barplot(x=x, y=y)"
                if kamus["type"] == "linechart":
                    mode = "L"
                    chartname = 'chartname = "line1.png"'
                    chartfunction = "sns.lineplot(x=x, y=y)"
                elif kamus["type"] == "piechart":
                    mode = "P"
                    chartname = 'chartname = "pie1.png"'
                    chartfunction = "plt.pie(y, labels = x, colors = warna_untuk_piechart, autopct='%.0f%%')"
                elif kamus["type"] == "donutchart":
                    mode = "D"
                    chartname = 'chartname = "donut1.png"'
                    chartfunction = "plt.pie(y, labels = x, autopct='%.0f%%', wedgeprops={'width': 0.5})"

                attrs = kamus["attrs"]
                for attr in attrs:
                    if attr.startswith("x="):
                        attr = attr.removeprefix("x=")
                        x = attr.split("/")
                        x = [f'"{item}"' if not item.isdigit() else item for item in x]
                        x = "[" + ", ".join(x) + "]"
                        templatecodes.append(f"x = {x}")
                    elif attr.startswith("y="):
                        attr = attr.removeprefix("y=")
                        y = attr.split("/")
                        y = [f'"{item}"' if not item.isdigit() else item for item in y]
                        y = "[" + ", ".join(y) + "]"
                        templatecodes.append(f"y = {y}")
                # templatecodes.append(f"sns.{tipechart}(x=x, y=y)")
                templatecodes.append(chartname)
                templatecodes.append(chartfunction)
                templatecodes.append(f"plt.title(chartname)")
                templatecodes.append(f"plt.savefig(chartname)")
                templatecodes.append(f"plt.show()")
                templatecodes.append(f"\n\n")

    print(templatecodes)
    a = "\n".join(templatecodes)
    content = kode_chart.replace("__TEMPLATE_CODE__", a)
    # print(content)
    # file_output = joiner(env_get('ULIBPY_DATA_FOLDER_ABS'), 'chart.py')
    # indah4(f'{file_output}',warna='cyan')
    # file_write(file_output, content)
    exec(content)


# TODO:
# ganti bentuk ke x=A,B,C,D,E|y=70,40,90,20,50 juga x=1:5 utk range
# masalahnya ini bagian dari decl language
chartlang = """
<canvas[cols=5](
    <piechart[x=A/B/C/D/E,y=70/40/90/20/50]
    <barchart[x=1/2/3/4/5,y=10/20/30/40/50]
    <linechart[x=1/2/3/4/5,y=10/20/30/40/50]
    <donutchart[x=A/B/C/D/E,y=70/40/90/20/50]
    <map
)
"""


def chartlang(code=chartlang):
    reset()
    process_language(code, current_handler=charthandler)
    pp(output)
    process_output(output)
