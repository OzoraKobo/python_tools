#! /usr/bin/env python3.7
# coding:utf-8
"""
@file     confFileMng.py
@brief    設定ファイル管理
@version  0.1
@author   SONODA Takehiko (OzoraKobo)
@details   
@date     2020/03/19 新規作成
"""

import os
import sys
import json
import time

# 処理結果定数
RESULT_SUCCESS          = 0
RESULT_CONF_INIT        = 1
RESULT_READ_ERROR       = 2
RESULT_WRITE_ERROR      = 3
RESULT_FILE_NOT_EXIST   = 4
RESULT_KEY_NOT_FOUND    = 5
RESULT_CONF_DICT_ERR    = 6
RESULT_UNKNOWN_ERR      = 7

# エラー内容
ErrorStr = [
    'Suceed',
    'Conf file initialize error',
    'Conf file read error',
    'Conf file write error',
    'Conf file not exist',
    'Key not found in conf dictionary',
    'Conf dictionary not exist',
    'Unknown error'
]

class ConfFileMng:
    """
    @class   ConfFileMng
    @brief   設定ファイル管理クラス
    @details 設定ファイルの保存・読み込み，設定項目の設定・取得を管理する
    @note    
    """
    def __init__(self, confFilePath = None, userConfDict = None, name = 'ConfFileMng', debug = False):
        """
        @fn      __init__()
        @brief   設定ファイル管理クラス(ConfFileMng)のコンストラクタ
        @param   self : 自クラスオブジェクト
        @param   confFilePath : 設定ファイルのパス名
        @param   userConfDict : ユーザ辞書の初期値
        @param   name : クラスオブジェクトの名前
        @param   debug : デバッグモード
        @return  None 戻り値なし
        @details 
        """
        # プロパティ
        self._confFilePath          = confFilePath      # 設定ファイルのパス名
        self._name                  = name              # クラスオブジクトの名前
        self._debug                 = debug             # デバッグモード
        # 定数
        self.RESULT_SUCCESS         = RESULT_SUCCESS
        self.RESULT_CONF_INIT       = RESULT_CONF_INIT
        self.RESULT_READ_ERROR      = RESULT_READ_ERROR
        self.RESULT_WRITE_ERROR     = RESULT_WRITE_ERROR
        self.RESULT_FILE_NOT_EXIST  = RESULT_FILE_NOT_EXIST
        self.RESULT_KEY_NOT_FOUND   = RESULT_KEY_NOT_FOUND
        self.RESULT_CONF_DICT_ERR   = RESULT_CONF_DICT_ERR
        self.RESULT_UNKNOWN_ERR     = RESULT_UNKNOWN_ERR
        # 設定辞書生成
        self._confDict              = dict()
        # 設定辞書
        if (userConfDict):
            # ユーザ設定辞書あり
            # 設定辞書を更新する
            self._confDict.update(userConfDict)
        self.debugPrint('instance created.\n')

    def debugPrint(self, msg):
        if (self._debug):
            sys.stdout.write(self._name + ' : ' + msg)

    def GetErrorStr(self, code):
        """
        @fn      GetErrorStr()
        @brief   エラー内容取得
        @param   self : 自クラスオブジェクト
        @param   code : エラーコード
        @return  エラーコードの意味を表す文字列
        @details エラーコードの意味を返す
        """
        try:
            errStr = ErrorStr[code]
        except:
            errStr = ErrorStr[self.RESULT_UNKNOWN_ERR]
        return self._name + ' : ' + errStr

    def PrintError(self, code):
        """
        @fn      PrintError()
        @brief   エラー内容出力
        @param   self : 自クラスオブジェクト
        @param   code : エラーコード
        @return  なし
        @details エラーコードの意味をstderrに出力する
        """
        sys.stderr.write(self.GetErrorStr(code) + '\n')

    def ConfRead(self):
        """
        @fn      ConfRead()
        @brief   設定をファイルから読み込む
        @param   self : 自クラスオブジェクト
        @return  処理結果
        @details 設定ファイルを読み込み設定辞書に反映する
        """
        # 設定ファイルの存在チェック
        if (os.path.exists(self._confFilePath) == False):
            # 設定ファイルなし
            self.debugPrint('ERROR Conf file not exsit. \'{0}\'\n'.format(self._confFilePath))
            return self.RESULT_FILE_NOT_EXIST

        # 設定ファイル読み込み
        try:
            with open(self._confFilePath, 'r', encoding='utf_8') as file:
                conf_read_json = json.load(file)
            self.debugPrint("Conf file read.\'{0}\'\n".format(self._confFilePath))
        except Exception as e:
            # ファイル読み込みエラー
            self.debugPrint('ERROR Conf file read. \'{0}\' ({1})\n'.format(self._confFilePath, e))
            return self.RESULT_READ_ERROR

        # 読み込んだ設定ファイルを設定辞書に反映する
        conf_read_dict = conf_read_json[0]
        if (self._confDict):
            # 設定辞書あり
            # 設定辞書を更新する
            self._confDict.update(conf_read_dict)
        else:
            # 設定辞書未生成
            self.debugPrint('ERROR Conf dictionary not created.\n')
            return self.RESULT_CONF_DICT_ERR

        # 正常終了
        return self.RESULT_SUCCESS

    def ConfSave(self):
        """
        @fn      ConfSave()
        @brief   設定をファイルに保存する
        @param   self : 自クラスオブジェクト
        @return  処理結果
        @details 設定辞書の内容をファイルに保存する
        """
        # JSONオブジェクト作成
        conf_json = [self._confDict]
        # 設定ファイル保存
        try:
            with open(self._confFilePath, 'w', encoding='utf_8') as file:
                json.dump(conf_json, file, indent=4)
            self.debugPrint("Conf file saved.\'{0}\'\n".format(self._confFilePath))
        except Exception as e:
            # ファイル書き込みエラー
            self.debugPrint("ERROR Conf file write. \'{0}\' ({1})\n".format(self._confFilePath, e))
            return self.RESULT_WRITE_ERROR
        # 正常終了
        return self.RESULT_SUCCESS

    def ConfSet(self, key, value, save = False):
        """
        @fn      ConfSet()
        @brief   設定辞書の設定値を更新する
        @param   self : 自クラスオブジェクト
        @param   key : 値を更新する設定辞書のキー
        @param   value : 設定辞書の値（更新値）
        @return  処理結果
        @details 指定されたkeyの設定辞書の値をvalueに更新する
        """
        if (self._confDict):
            # 設定辞書あり
            # 設定辞書を更新する
            _dict = { key : value }
            self._confDict.update(_dict)
            self.debugPrint('Conf update \'{0}\' = \'{1}\'\n'.format(key, self._confDict[key]))
        else:
            # 設定辞書未生成
            self.debugPrint('ERROR Conf dictionary not created.\n')
            return self.RESULT_CONF_DICT_ERR

        # 正常終了
        return self.RESULT_SUCCESS

    def ConfGet(self, key):
        """
        @fn      ConfGet()
        @brief   設定辞書の設定値を取得する
        @param   self : 自クラスオブジェクト
        @param   key : 値を取得する設定辞書のキー
        @return  値 keyが未力なかったときは None
        @details 指定されたkeyの設定辞書の値を返す
        """
        result = self.RESULT_SUCCESS
        value = None
        if (self._confDict):
            # 設定辞書あり
            if (key in self._confDict):
                # キーが設定辞書に存在
                # 値を取得する
                value = self._confDict[key]
                self.debugPrint('Conf get \'{0}\' = \'{1}\'\n'.format(key, value))
            else:
                # キーが設定辞書にない
                self.debugPrint('ERROR key=\'{0}\' not exist in Conf Dictionary.\n'.format(key))
                result = self.RESULT_KEY_NOT_FOUND
        else:
            # 設定辞書未生成
            self.debugPrint('ERROR Conf dictionary not created.\n')
            result = self.RESULT_CONF_DICT_ERR

        # リターン
        return result, value

if __name__ == '__main__':

    test_dict = { 'id' : 'test', 'prm1': 'abcd', 'prm2': '1234' }

    test_conf = ConfFileMng(confFilePath = './test_conf.json', userConfDict = test_dict, name = 'ConfFileTest', debug = False)

    result, id = test_conf.ConfGet('id')
    result, prm1 = test_conf.ConfGet('prm1')
    result, prm2 = test_conf.ConfGet('prm2')
    print('[Init] id: {0}, prm1: {1}, prm2: {2}'.format(id, prm1, prm2))

    result = test_conf.ConfRead()
    if (result == test_conf.RESULT_SUCCESS):
        result, id = test_conf.ConfGet('id')
        result, prm1 = test_conf.ConfGet('prm1')
        result, prm2 = test_conf.ConfGet('prm2')
        print('[Read1] id: {0}, prm1: {1}, prm2: {2}'.format(id, prm1, prm2))
    else:
        test_conf.PrintError(result)
        result = test_conf.ConfSave()
        if (result != test_conf.RESULT_SUCCESS):
            test_conf.PrintError(result)

    test_conf.ConfSet('prm1', 'ABCD')
    test_conf.ConfSet('prm2', '5678')
    result, id = test_conf.ConfGet('id')
    result, prm1 = test_conf.ConfGet('prm1')
    result, prm2 = test_conf.ConfGet('prm2')
    print('[Update] id: {0}, prm1: {1}, prm2: {2}'.format(id, prm1, prm2))

    result = test_conf.ConfSave()
    if (result != test_conf.RESULT_SUCCESS):
        test_conf.PrintError(result)

    result = test_conf.ConfRead()
    if (result == test_conf.RESULT_SUCCESS):
        result, id = test_conf.ConfGet('id')
        result, prm1 = test_conf.ConfGet('prm1')
        result, prm2 = test_conf.ConfGet('prm2')
        print('[Read2] id: {0}, prm1: {1}, prm2: {2}'.format(id, prm1, prm2))

