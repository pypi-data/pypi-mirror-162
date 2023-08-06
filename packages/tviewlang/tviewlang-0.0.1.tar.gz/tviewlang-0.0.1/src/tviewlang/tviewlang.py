import os, sys
from pprint import pprint as pp
from uuid import uuid4 as u4

from declang.processor import process_language
from langutils.app.fileutils import file_write
from langutils.app.printutils import indah4
from langutils.app.stringutils import tabify_contentlist_space
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

output = {}


def reset():
    global output
    output.clear()


def handler(tree, parent=""):
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
            if namaparent == "main":
                print("tag main!")
            elif namaparent == "form":
                print("tag form", "parent:", parent)
                output["form"] = {}
            elif namaparent == "input":
                print("tag input", "parent:", parent)
                if parent == "form":
                    output["form"][itemid] = {"type": "input", "children": []}
            elif namaparent == "area":
                print("tag area", "parent:", parent)
                output["form"][itemid] = {"type": "area", "children": []}
            elif namaparent == "pass":
                print("tag pass", "parent:", parent)
                output["form"][itemid] = {"type": "pass", "children": []}
            elif namaparent == "check":
                print("tag check", "parent:", parent)
                output["form"][itemid] = {"type": "check", "children": []}
            elif namaparent == "combo":
                print("tag combo", "parent:", parent)
                output["form"][itemid] = {"type": "combo", "children": []}
            elif namaparent == "button":
                print("tag button", "parent:", parent)
                output["form"][itemid] = {"type": "button", "children": []}
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
                    output["form"][itemid]["children"].append(f"{k}={v}")
                elif jenis2 == "item_key_value_berslash":
                    pass
                elif jenis2 == "item_key_value_boolean":
                    nilai = token(tupleitem)
                    print(f"  attr {namaparent}/{itemid} bool => {nilai}")
                    output["form"][itemid]["children"].append(nilai)
        elif jenis == "element_children":
            for tupleitem in anak(item):
                for anaktupleitem in tupleitem:
                    res = handler(anaktupleitem, parent=namaparent)
        elif jenis == "cdata_text":
            pass


gocode = """
package main

import (
	"github.com/rivo/tview"
)

func main() {
	app := tview.NewApplication()

__TEMPLATE_CODE__

	if err := app.SetRoot(mainwidget, true).EnableMouse(true).Run(); err != nil {
		panic(err)
	}
}
"""


def process_output(output, output_file):
    template_codes = []

    for k, v in output.items():

        if k == "form":
            kode = "mainwidget := tview.NewForm()"
            template_codes.append(kode)

            for l, w in output["form"].items():
                if w["type"] == "input":
                    lebar = 20
                    label, value = "", ""
                    for anak in w["children"]:
                        if "=" in anak:  # label=value
                            label, value = anak.split("=")
                        elif anak == "w":  # w=10
                            lebar = anak
                    kode = f'mainwidget.AddInputField("{label}", "{value}", {lebar}, nil, nil)'
                elif w["type"] == "combo":
                    pertama, sisa = w["children"][0], w["children"][1:]
                    sisa = ", ".join([f'"{item}"' for item in sisa])
                    kode = f'mainwidget.AddDropDown("{pertama}", []string{{{sisa}}}, 0, nil)'
                elif w["type"] == "pass":
                    label = ""
                    lebar = 20
                    # label = w['children'][0]
                    # if '=' in label:
                    #     label, nilai = label.split('=')
                    for anak in w["children"]:
                        if "=" in anak:  # label=value
                            label, value = anak.split("=")
                        elif anak == "w":  # w=10
                            lebar = anak
                        else:
                            label = anak
                    kode = f"""mainwidget.AddPasswordField("{label}", "", {lebar}, '*', nil)"""
                elif w["type"] == "check":
                    label, check = w["children"][0].replace("_", " "), int(
                        w["children"][1]
                    )
                    check = "true" if check == 1 else "false"
                    kode = f'mainwidget.AddCheckbox("{label}", {check}, nil)'
                elif w["type"] == "button":
                    label = ""
                    if w["children"]:
                        label = w["children"][0].replace("_", " ")
                    kode = f'mainwidget.AddButton("{label}", nil)'
                template_codes.append(kode)

    template_codes = tabify_contentlist_space(template_codes, num_tab=1, space_size=4)
    content = gocode.replace("__TEMPLATE_CODE__", template_codes)
    file_write(output_file, content)


tviewcode = """
<header<footer<sidebar<rightbar
<main(
    <form(
        <input[name=myinput]
        <pass[name=myarea]
        <check[Masukkan_yang_saya_minta,0]
        <combo[enam,tujuh,delapan,sembilan]
        <button[Tekan_aku]
    )
)
"""


def tviewlang(code=tviewcode, output_file='runme.go'):
    reset()
    process_language(code, current_handler=handler)
    pp(output)
    process_output(output, output_file=output_file)
