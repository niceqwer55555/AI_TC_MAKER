import requests,json
session=requests.session()
import sys,os
sys.path.append(os.getcwd())
from parseExcel import OperateExcel
current_dir = os.getcwd()


def addWebtestcase(data):
    API = "http://127.0.0.1:8888/api/generate/"
    headers = {"Content-Type": "application/json"}
    payload = {
        "provider":"openai",
        "prompt":data
    }

    res=session.post(API,headers=headers,json=payload,verify=False)
    steps = json.loads(res.text).get('testcases')[0].get('steps')
    # print(res.text)
    # print(web_testcase_code)
    return  steps


if __name__=="__main__":
    import json
    contents = 'test.xlsx'
    # path = current_dir + "/apache-jmeter-5.1.1/data/" + contents
    path = 'D:/PY/AI_TC_MAKER-main/'+ contents
    # path = contents
    test=OperateExcel(path)

    read_columns_data_list = test.read_columns_data() #特别注意应用问题
    id_list1 = read_columns_data_list[0]
    for id in id_list1:
        dd = test.find_column_value(id)
        # print(dd)
        web_testcase_code_list = []
        execute_list = []
        modify_list = []
      #  payload = []
        for column in dd:
            data_all = test.test_data(column)[0]
            # print(data_all)
            web_testcase_code_list.append(data_all.get('用例标题'))
            execute_list.append(data_all.get('步骤'))
            modify_list.append(data_all.get('预期'))
        for column1 in dd:
            print(column1)
            try:
                cc = addWebtestcase(modify_list[column1-2])
                test.write_to_excel(path,8,column1,cc)
            except:
                pass



