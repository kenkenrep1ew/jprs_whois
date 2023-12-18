# !!!出力をエクセルファイルに合わせて拡張する用。ドメインの洗い出しだけであれば実行は必要なし。ドメインの細部情報を埋めるためのもの。
# whois.jprs.jpで検索タイプ[ドメイン名情報]により[検索キーワード]を用いて検索した実行結果を取得する。
# 本スクリプトは、search_by_org.pyの出力ファイルoutput_searched_by_org_YYYYMMDD_HHMM.txtを入力に取る。
# output_searched_by_org_YYYYMMDD_HHMM.txtの各行からドメインを取り出し、検索キーワードとする。
# 例：有限責任監査法人トーマツ;(Deloitte Touche Tohmatsu LLC);TOHMATSU.CO.JP　の3つめの値。

import re
import argparse
import datetime
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def select_search_type(driver):
    select_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "type"))
    )
    select = Select(select_element)
    select.select_by_value('DOM')

def enter_search_keyword(driver, keyword):
    search_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "key"))
    )
    search_box.clear()
    search_box.send_keys(keyword)
    search_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//input[@type='submit']"))
    )
    search_button.click()

def process_pre_text(pre_text, keyword):
    if keyword.endswith(".co.jp") or keyword.endswith(".CO.JP"):
        return process_pre_text_cojp(pre_text)
    else:
        return process_pre_text_not_cojp(pre_text)

def process_pre_text_not_cojp(pre_text):
    # '[Domain Name]' の部分を抜き出す
    domain_name_match = re.search(r'\[Domain Name\]\s*([^\n\r]+)', pre_text)
    # '[登録者名]' の部分を抜き出す
    registrant_name_match = re.search(r'\[登録者名\]\s*([^\n\r]+)', pre_text)
    # '[Registrant]' の部分を抜き出す
    registrant_match = re.search(r'\[Registrant\]\s*([^\n\r]+)', pre_text)

    if domain_name_match and registrant_name_match and registrant_match:
        return f"{registrant_name_match.group(1)};{registrant_match.group(1)};{domain_name_match.group(1)}"
    return ""

def process_pre_text_cojp(pre_text):
    # 'a. [ドメイン名]' の部分を抜き出す
    domain_name_match = re.search(r'a\.\s*\[ドメイン名\]\s*([^\n\r]+)', pre_text)
    # 'f. [組織名]' の部分を抜き出す
    org_name_match = re.search(r'f\.\s*\[組織名\]\s*([^\n\r]+)', pre_text)
    # 'g. [Organization]' の部分を抜き出す
    organization_match = re.search(r'g\.\s*\[Organization\]\s*([^\n\r]+)', pre_text)

    if domain_name_match and org_name_match and organization_match:
        return f"{org_name_match.group(1)};{organization_match.group(1)};{domain_name_match.group(1)}"
    return ""


# コマンドライン引数の設定
parser = argparse.ArgumentParser(description='JPRS WHOIS Search Keywords File')
parser.add_argument('file_path', help='File path containing search keywords')
args = parser.parse_args()

# 現在の日付と時刻を取得し、ファイル名に組み込む
current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M")
output_filename = f"output_searched_by_url_{current_time}.txt"

# Webドライバの設定
driver = webdriver.Chrome()

try:
    driver.get("https://whois.jprs.jp/")
    select_search_type(driver)

    with open(args.file_path, 'r', encoding='utf-8') as file, \
         open(output_filename, 'w', encoding='utf-8') as output_file:
        for line in file:
            # 各行の最後の部分を検索キーワードとして使用
            keyword = line.strip().split(';')[-1]
            if keyword:
                enter_search_keyword(driver, keyword)

                try:
                    WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located((By.TAG_NAME, "pre"))
                    )
                    pre_text = driver.find_element(By.TAG_NAME, "pre").text
                    processed_text = process_pre_text(pre_text, keyword)
                    if processed_text:
                        print(f"Results for '{keyword}':\n{processed_text}\n")
                        output_file.write(f"{processed_text}\n")
                    # else:
                    #     print(f"No relevant data found for '{keyword}'.\n")
                    #     output_file.write(f"No relevant data found for '{keyword}'.\n\n")
                except TimeoutException:
                    print(f"No data found for '{keyword}'.\n")
                    # output_file.write(f"No data found for '{keyword}'.\n\n")

                time.sleep(10)

finally:
    driver.quit()
