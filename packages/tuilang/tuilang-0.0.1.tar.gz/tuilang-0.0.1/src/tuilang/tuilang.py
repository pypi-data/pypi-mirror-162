import os, sys
from pprint import pprint as pp
from uuid import uuid4 as u4

from langutils.app.printutils import indah4
from langutils.app.treeutils import (
    anak,
    data,
    token,
    child1,
    child2,
    child3,
    child4,
    child,
    chdata,
    chtoken,
    ispohon,
    istoken,
    beranak,
    sebanyak,
    jumlahanak,
)
from langutils.app.dirutils import joiner
from langutils.app.fileutils import file_write
from langutils.app.utils import env_get
from langutils.app.stringutils import tabify_content_space, tabify_contentlist_space
from declang.processor import process_language

from rich.console import RenderableType
from rich.syntax import Syntax
from rich.table import Table
from rich.traceback import Traceback
from rich.layout import Layout

# from textual.app import App
# from textual.reactive import Reactive
# from textual.widgets import (
#     Header, Footer,
#     FileClick, DirClick,
#     ScrollView, Static, Placeholder,
#     DirectoryTree,
# )
# from textual.widget import Widget
# from textual.views import GridView

from rich.pretty import pprint

template_kode = """
from rich.console import RenderableType
from rich.syntax import Syntax
from rich.table import Table
from rich.traceback import Traceback
from rich.layout import Layout

from rich import box
from rich.align import Align
from rich.panel import Panel

from textual.app import App
from textual.reactive import Reactive
from textual.widgets import (
    Header, Footer, 
    FileClick, DirClick, 
    ScrollView, Static, Placeholder,
    DirectoryTree,
)
from textual.widget import Widget
from textual.views import GridView

class MyApp(App):
    async def on_load(self) -> None:
        # await self.bind("b", "view.toggle('sidebar')", "Sidebar")
        await self.bind("q", "quit", "Quit")
        await self.bind("escape", "quit", "Quit")
    async def on_mount(self) -> None:
        # bikin table 5x5
        tbl = Table.grid(padding=1, expand=True)
        tbl.add_column(style='on green')
        tbl.add_column()
        tbl.add_column(style='on magenta')
        tbl.add_column()
        tbl.add_column(style='on yellow')
        for i in range(5):
            # tbl.add_row(get_by_datatypes('string'), get_by_datatypes('string'), get_by_datatypes('string'), get_by_datatypes('string'), get_by_datatypes('string'))
            tbl.add_row(
                Placeholder(name=f'{i},1'),
                Placeholder(name=f'{i},2'),
                Placeholder(name=f'{i},3'),
                Placeholder(name=f'{i},4'),
                Placeholder(name=f'{i},5'),
            )
        grid = await self.view.dock_grid(edge="top", name="body")

__TEMPLATE_BARIS__

__TEMPLATE_KOLOM__

__TEMPLATE_AREA1__

__TEMPLATE_AREA2__

MyApp.run(title="Gitor")

"""

kode_output = template_kode

areanum = 0


def handler(tree, parent="", parentid=None):
    global areanum
    kembali = ""
    name, attrs, children, text = "", "", "", ""
    namaparent = ""
    itemid = ""
    for item in anak(tree):
        jenis = data(item)
        if jenis == "element_name":
            namaparent = token(item)
            itemid = str(u4())
            print("elem:", namaparent)
            if namaparent == "layout":
                print("<layout>")
            elif namaparent == "content":
                print("<content>", "parent:", parent)
                output["content"] = {}
                output["columns"] = {"attrs": {}, "ids": {}}
                output["rows"] = {"attrs": {}, "ids": {}}
            elif namaparent == "row":
                print(f"<row>, id={itemid}", "parent:", parent)
                if parent == "content":
                    output["content"][itemid] = {"type": "row", "cols": {}}
                    # row ke content, sekarang semua content punya id sama
                    output["rows"]["ids"][itemid] = parentid
            elif namaparent == "col":
                print(f"<col>, id={itemid}", "parent:", parent, parentid)
                areanum += 1
                print("           area:", areanum)
                if parent == "row" and parentid in output["content"]:
                    control = {"type": "col"}
                    output["content"][parentid]["cols"][itemid] = control
                    # agar bisa peroleh row dari col, buat assoc, colid = rowid
                    output["columns"]["ids"][itemid] = parentid

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
                    print(
                        f"  attr of {namaparent}/{itemid}, row={parentid} k=v => {k}={v}"
                    )
                    if namaparent == "col":
                        output["content"][parentid]["cols"][itemid][k] = v
                        if not k in output["columns"]["attrs"]:
                            output["columns"]["attrs"][k] = []
                        output["columns"]["attrs"][k].append(v)
                    elif namaparent == "row":
                        output["content"][itemid][k] = v
                        if not k in output["rows"]["attrs"]:
                            output["rows"]["attrs"][k] = []
                        output["rows"]["attrs"][k].append(v)

                elif jenis2 == "item_key_value_boolean":
                    nilai = token(tupleitem)
                    print(f"  attr {namaparent}/{itemid} bool => {nilai}")
                    if namaparent == "col":
                        output["content"][parentid]["cols"][itemid][nilai] = True
                        if not "booleans" in output["cols"]["attrs"]:
                            output["cols"]["attrs"]["booleans"] = []
                        output["cols"]["attrs"]["booleans"].append(nilai)
                    elif namaparent == "row":
                        output["content"][itemid][nilai] = True
                        if not "booleans" in output["rows"]["attrs"]:
                            output["rows"]["attrs"]["booleans"] = []
                        output["rows"]["attrs"]["booleans"].append(nilai)
        elif jenis == "element_children":
            for tupleitem in anak(item):
                for anaktupleitem in tupleitem:
                    res = handler(anaktupleitem, parent=namaparent, parentid=itemid)
        elif jenis == "cdata_text":
            pass


output = {}


default_code = """
<layout(
    <content(
        <row[fraction=1](
            <col[fraction=3]
            <col[fraction=7]
        )
        <row[fraction=6](
            <col
            <col
        )
        <row[fraction=2](
            <col
            <col
        )
        <row[fraction=1](
            <col
            <col
        )
    )
)
"""

def tuilang(code=default_code, output_file='runme.py'):
    global kode_output

    process_language(code, current_handler=handler,)

    pprint(output)

    areas = len(output["columns"]["ids"])
    rows = len(output["rows"]["ids"])
    colnum = 0
    for k, v in output["content"].items():
        colnum = max(colnum, len(v["cols"].keys()))

    rowscode = []
    for i in range(rows):
        fr = 1
        if "fraction" in output["rows"]["attrs"]:
            if len(output["rows"]["attrs"]["fraction"]) > i:
                fr = output["rows"]["attrs"]["fraction"][i]
        kode = f"grid.add_row(fraction={fr}, name='row{i+1}')"
        print(kode)
        rowscode.append(kode)

    # hasil_baris = '\n'.join(rowscode)
    hasil_baris = tabify_contentlist_space(rowscode, num_tab=2, space_size=4)
    kode_output = kode_output.replace("__TEMPLATE_BARIS__", hasil_baris)
    colscode = []
    for i in range(colnum):
        fr = 1
        if "fraction" in output["columns"]["attrs"]:
            if len(output["columns"]["attrs"]["fraction"]) > i:
                fr = output["columns"]["attrs"]["fraction"][i]
        kode = f"grid.add_column(fraction={fr}, name='col{i+1}')"
        print(kode)
        colscode.append(kode)

    # hasil_kolom = '\n'.join(colscode)
    hasil_kolom = tabify_contentlist_space(colscode, num_tab=2, space_size=4)
    kode_output = kode_output.replace("__TEMPLATE_KOLOM__", hasil_kolom)
    areas1code = []
    k = 0
    for i in range(rows):
        for j in range(colnum):
            k += 1
            kode = f"area{k}='col{j+1},row{i+1}'"
            areas1code.append(kode)

    gabung1 = ", ".join(areas1code)
    hasil_area1 = f"grid.add_areas({gabung1})"
    print(hasil_area1)
    # hasil_area1 = '\n'.join(colscode)
    hasil_area1b = tabify_content_space(hasil_area1, num_tab=2, space_size=4)
    kode_output = kode_output.replace("__TEMPLATE_AREA1__", hasil_area1b)

    areas2code = []
    k = 0
    for i in range(rows):
        for j in range(colnum):
            k += 1
            control = f"Placeholder(name='{i+1}{j+1}')"
            kode = f"area{k}={control}"
            areas2code.append(kode)

    gabung2 = ", ".join(areas2code)
    hasil_area2 = f"grid.place({gabung2})"
    print(hasil_area2)
    hasil_area2b = tabify_content_space(hasil_area2, num_tab=2, space_size=4)
    kode_output = kode_output.replace("__TEMPLATE_AREA2__", hasil_area2b)
    file_write(output_file, kode_output)
    print(kode_output)

