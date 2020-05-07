#! /usr/bin/env python3.7
# coding:utf-8
"""
@file       ConfFileMng.py
@brief      設定ファイル管理
@version    0.30
@author     SONODA Takehiko (OzoraKobo)
@copyright  Copyright (c) SONODA Takehiko 2020
@details   
@date       2020/03/20 v0.10 新規作成
@date       2020/03/20 v0.20 例外の送出機能追加
@date       2020/04/18 v0.30 設定辞書の設定値を更新メソッド(ConfSet)で、設定ファイルに保存できない問題修正
@date       2020/04/18 v0.30 設定辞書をユーザ定義辞書に置き換えるメソッド(ConfReset)追加
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

class ConfDictNotFoundError(Exception):
    """Conf dictionary not exist"""
    pass

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
        # エラーコード
        self._errorCode             = self.RESULT_SUCCESS
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

    def GetErrorStr(self):
        """
        @fn      GetErrorStr()
        @brief   エラー内容取得
        @param   self : 自クラスオブジェクト
        @return  エラーコードの意味を表す文字列
        @details エラーコードの意味を返す
        """
        try:
            errStr = ErrorStr[self._errorCode]
        except:
            errStr = ErrorStr[self.RESULT_UNKNOWN_ERR]
        return self._name + ' : ' + errStr

    def PrintError(self):
        """
        @fn      PrintError()
        @brief   エラー内容出力
        @param   self : 自クラスオブジェクト
        @return  なし
        @details エラーコードの意味をstderrに出力する
        """
        sys.stderr.write(self.GetErrorStr() + '\n')

    def ConfRead(self):
        """
        @fn      ConfRead()
        @brief   設定をファイルから読み込む
        @param   self : 自クラスオブジェクト
        @return  なし
        @details 設定ファイルを読み込み設定辞書に反映する
        """
        self._errorCode = self.RESULT_SUCCESS
        # 設定ファイル読み込み
        try:
            with open(self._confFilePath, 'r', encoding='utf_8') as file:
                conf_read_json = json.load(file)
        except FileNotFoundError as e:
            # ファイルが存在しない
            self.debugPrint('ERROR Conf file not exist. \'{0}\'\n'.format(self._confFilePath))
            self._errorCode = self.RESULT_FILE_NOT_EXIST
            raise Exception('{0} : {1}'.format(self._name, e))
        except Exception as e:
            # ファイルが存在しない
            self.debugPrint('ERROR Conf file read. \'{0}\'\n'.format(self._confFilePath))
            self._errorCode = self.RESULT_READ_ERROR
            raise Exception('{0} : {1}'.format(self._name, e))
        else:
            self.debugPrint("Conf file read.\'{0}\'\n".format(self._confFilePath))

        # 読み込んだ設定ファイルを設定辞書に反映する
        conf_read_dict = conf_read_json[0]
        if (self._confDict != None):
            # 設定辞書あり
            # 設定辞書を更新する
            self._confDict.update(conf_read_dict)
        else:
            # 設定辞書未生成
            self.debugPrint('ERROR Conf dictionary not exist.\n')
            self._errorCode = self.RESULT_CONF_DICT_ERR
            raise ConfDictNotFoundError('{0} : Conf dictionary not exist.'.format(self._name))

    def ConfSave(self):
        """
        @fn      ConfSave()
        @brief   設定をファイルに保存する
        @param   self : 自クラスオブジェクト
        @return  なし
        @details 設定辞書の内容をファイルに保存する
        """
        self._errorCode = self.RESULT_SUCCESS
        # JSONオブジェクト作成
        conf_json = [self._confDict]
        # 設定ファイル保存
        try:
            with open(self._confFilePath, 'w', encoding='utf_8') as file:
                json.dump(conf_json, file, indent=4)
            self.debugPrint("Conf file saved.\'{0}\'\n".format(self._confFilePath))
        except Exception as e:
            # ファイル書き込みエラー
            self.debugPrint("ERROR Conf file write. \'{0}\'\n".format(self._confFilePath))
            self._errorCode = self.RESULT_WRITE_ERROR
            raise Exception('{0} : {1}'.format(self._name, e))

    def ConfSet(self, key, value, save = False):
        """
        @fn      ConfSet()
        @brief   設定辞書の設定値を更新する
        @param   self  : 自クラスオブジェクト
        @param   key   : 値を更新する設定辞書のキー
        @param   value : 設定辞書の値（更新値）
        @param   save  : 設定値変更後、設定ファイルに保存するフラグ True=ファイル保存，False=ファイル保存しない
        @return  なし
        @details 指定されたkeyの設定辞書の値をvalueに更新する
        """
        self._errorCode = self.RESULT_SUCCESS
        if (self._confDict != None):
            # 設定辞書あり
            # 設定辞書を更新する
            _dict = { key : value }
            try:
                self._confDict.update(_dict)
            except:
                self.debugPrint('Conf update \'{0}\' = \'{1}\'\n'.format(key, self._confDict[key]))
                raise Exception('{0} : Conf update \'{1}\' = \'{2}\'\n'.format(self._name, key, self._confDict[key]))
            else:
                # 設定ファイル保存
                if (save):
                    self.ConfSave()
        else:
            # 設定辞書未生成
            self.debugPrint('ERROR Conf dictionary not exist.\n')
            self._errorCode = self.RESULT_CONF_DICT_ERR
            raise ConfDictNotFoundError('{0} : Conf dictionary not exist.'.format(self._name))

    def ConfReset(self, userConfDict = None, save = False):
        """
        @fn      ConfReset()
        @brief   設定辞書をユーザ定義辞書に置き換える
        @param   self : 自クラスオブジェクト
        @param   userConfDict : ユーザ辞書
        @return  処理結果
        @details 辞書をユーザ辞書に置き換える
        """
        # 設定辞書
        if (userConfDict):
            # ユーザ設定辞書あり
            # 設定辞書再生成
            self._confDict  = None
            self._confDict  = dict()
            # 設定辞書を更新する
            self._confDict.update(userConfDict)
            self.debugPrint('Conf renewed.\n')
            # 設定ファイル保存
            if (save):
                self.ConfSave()

    def ConfGet(self, key):
        """
        @fn      ConfGet()
        @brief   設定辞書の設定値を取得する
        @param   self : 自クラスオブジェクト
        @param   key : 値を取得する設定辞書のキー
        @return  値 keyが未力なかったときは None
        @details 指定されたkeyの設定辞書の値を返す
        """
        self._errorCode = self.RESULT_SUCCESS
        value = None
        if (self._confDict != None):
            # 設定辞書あり
            try:
                value = self._confDict[key]
            except:
                # キーが設定辞書にない
                self.debugPrint('ERROR key=\'{0}\' not exist in Conf Dictionary.\n'.format(key))
                self._errorCode = self.RESULT_KEY_NOT_FOUND
                raise Exception('{0} : key=\'{1}\' not exist in Conf Dictionary.\n'.format(self._name, key))
            else:
                self.debugPrint('Conf get \'{0}\' = \'{1}\'\n'.format(key, value))                
        else:
            # 設定辞書未生成
            self.debugPrint('ERROR Conf dictionary not exist.\n')
            self._errorCode = self.RESULT_CONF_DICT_ERR
            raise ConfDictNotFoundError('{0} : Conf dictionary not exist.'.format(self._name))

        # リターン
        return value

if __name__ == '__main__':

    test_dict = { 'id' : 'test', 'prm1': 'abcd', 'prm2': '1234' }

    test_conf = ConfFileMng(confFilePath = './test_conf.json', userConfDict = test_dict, name = 'ConfFileTest', debug = False)

    try:
        id = test_conf.ConfGet('id')
        prm1 = test_conf.ConfGet('prm1')
        prm2 = test_conf.ConfGet('prm2')
    except Exception as e:
        print(e)
        exit(1)
    else:
        print('[Init] id: {0}, prm1: {1}, prm2: {2}'.format(id, prm1, prm2))

    try:
        test_conf.ConfRead()
    except Exception as e:
        print(e)
        test_conf.ConfSave()
    else:
        id = test_conf.ConfGet('id')
        prm1 = test_conf.ConfGet('prm1')
        prm2 = test_conf.ConfGet('prm2')
        print('[Read1] id: {0}, prm1: {1}, prm2: {2}'.format(id, prm1, prm2))

    try:
        test_conf.ConfSet('prm1', 'ABCD')
        test_conf.ConfSet('prm2', '5678')
    except Exception as e:
        print(e)
        exit(1)

    try:
        id = test_conf.ConfGet('id')
        prm1 = test_conf.ConfGet('prm1')
        prm2 = test_conf.ConfGet('prm2')
    except Exception as e:
        print(e)
        exit(1)
    else:
        print('[Update] id: {0}, prm1: {1}, prm2: {2}'.format(id, prm1, prm2))

    try:
        test_conf.ConfSave()
    except Exception as e:
        print(e)
        exit(1)

    try:
        test_conf.ConfRead()
    except Exception as e:
        print(e)
        exit(1)
    else:    
        id = test_conf.ConfGet('id')
        prm1 = test_conf.ConfGet('prm1')
        prm2 = test_conf.ConfGet('prm2')
        print('[Read2] id: {0}, prm1: {1}, prm2: {2}'.format(id, prm1, prm2))

