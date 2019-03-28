# coding: utf-8

import os
import sys
import uuid
import hashlib
import time
import requests
import json
import base64
from  urllib.parse import urlencode,quote
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget,QFileDialog
from PyQt5.QtGui import QIcon
from PyQt5.uic import loadUi
from . import from_to_type
from .fileutil import get_file_realpath,check_and_create


class kdYoudaoVoiceAssistant(QWidget):
    def __init__(self):
        super(kdYoudaoVoiceAssistant, self).__init__()
        loadUi(get_file_realpath("kdYoudaoVoiceAssistant.ui"), self)
        self.setWindowIcon(QIcon(get_file_realpath('data/Dictionary-icon.png')))
        

#         for translate_type in from_to_type.translate_types:
#             self.cb_from_to.addItem(translate_type[1])

        appKey_config_file = get_file_realpath("appKey_config.json")
        check_and_create(appKey_config_file)
        with open(appKey_config_file, "r",encoding="utf-8") as f:
            content = f.read().strip()
            if content != "":
                conf = json.loads(content)
                self.appKey = conf["appKey"]
                self.secret_key = conf["secret_key"]

    @pyqtSlot()
    def on_pb_open_file_clicked(self):
        fileName1, _ = QFileDialog.getOpenFileName(self,
                                    "选择文件",
                                    os.environ["HOME"],
                                    "All Files (*.wav)")   #设置文件扩展名过滤,注意用双分号间隔
        if fileName1:
            self.voice_file = fileName1
            self.tb_result.setText(fileName1)

    @pyqtSlot()
    def on_pb_transfer_to_text_clicked(self):
        with open(self.voice_file,"rb") as vf:
            vf_ctx = vf.read()
            self.vf_base64 = base64.b64encode(vf_ctx)
            print(self.vf_base64)
#             self.tb_result.setText(str(self.vf_base64,encoding="utf-8"))
            self._translate(str(self.vf_base64,encoding="utf-8"))
            

    # ～ 免费的调用模式
#     接口文档地址：https://ai.youdao.com/docs/doc-asr-api.s#p02,https://ai.youdao.com/docs/doc-asr-api.s#p17
    def _translate(self,vf_base64):
        params = {}

        salt = str(uuid.uuid1())
#        langType， 英文：en
        params["langType"] = "zh-CHS"
        params["appKey"] = self.appKey
        params["salt"] = salt
        sign_source = str(self.appKey + vf_base64 + salt  + self.secret_key).encode()
        m = hashlib.md5()
        m.update(sign_source)
        sign = str(m.hexdigest()).upper()
        self.tb_result.append("sign:"+sign)
        self.tb_result.moveCursor(self.tb_result.textCursor().End)
        params["sign"]=str(sign)
        params["format"]="wav"
#         采样率，8000或16000
        params["rate"] = "8000"
        params["channel"] = "1"
        params["type"] = "1"
#         params["q"] = quote(vf_base64,'utf-8')[:1024]
        params["q"] = quote(vf_base64,'utf-8')
        print("入參:",params)
        self.tb_result.append("入參:"+str(params))
        self.tb_result.moveCursor(self.tb_result.textCursor().End)
        r = requests.post(
            "http://openapi.youdao.com/asrapi", params=params)
        print("结果："+r.text)
        self.tb_result.append("结果："+r.text)
        self.tb_result.moveCursor(self.tb_result.textCursor().End)
        result = json.loads(r.text)

        if result["errorCode"] != "0":
            pass
        show_result = result["result"]
        self.tb_result.append(show_result)
        self.tb_result.moveCursor(self.tb_result.textCursor().End)
    # ～ 调用个人的API key来查询，收费

    def _translate_detail(self):
        word = self.le_word.text().strip()
        if word == "":
            pass

        salt = str(uuid.uuid1())
        now = str(int(time.time()))
        input_word = None
        if len(word) > 20:
            input_word = word[:10] + str(len(word))+word[11:]
        else:
            input_word = word

        params = {}
        cur_type = self.cb_from_to.currentText()
        for translate_type in from_to_type.translate_types:
            if translate_type[1] == cur_type:
                origin_type = translate_type[0].replace("ZH_CN","zh-CHS").replace("KR","ko")
                types = origin_type.split("2")
                params["from"] = types[0].lower()
                params["to"] = types[1].lower()

        params["q"] = word
        params["appKey"] = self.appKey
        params["salt"] = salt
        sign_source = str(self.appKey + input_word + salt + now + self.secret_key).encode()
        params["sign"]=str(hashlib.sha256(sign_source).hexdigest())
        params["signType"] = "v3"
        params["curtime"] = now
        print("入參:",params)
        r = requests.get(
            "https://openapi.youdao.com/api", params=params)
        result = json.loads(r.text)
        print("结果："+r.text)

        if result["errorCode"] != "0":
            pass
        show_result = result["translation"][0]
        if "web" in result.keys():
            show_result += "\n网络释义:\n"
            web = result["web"]
            for w in web:
                show_result = show_result + "    " + \
                    w["key"] + "," + ",".join(w["value"]) + "\n"
        self.tb_result.setText(show_result)


def main():
    app = QtWidgets.QApplication(sys.argv)
    win = kdYoudaoVoiceAssistant()
    win.show()
    sys.exit(app.exec_())
