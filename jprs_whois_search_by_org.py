# whois.jprs.jpで検索タイプ[ドメイン名情報(登録者名)]により[検索キーワード]を用いて検索した実行結果を取得する。
# 本スクリプトは、実行時に1行に1件の検索キーワードが記載されているテキストファイルを入力に取る。
# $python3 search_by_org.py keywords.txt
# 本スクリプトは、検索結果があった場合、output_searched_by_org_YYYYMMDD_HHMM.txtに出力する。
# 出力の形式は、　有限責任監査法人トーマツ;(Deloitte Touche Tohmatsu LLC);TOHMATSU.CO.JP
# 実行時、短時間に複数件続けて検索した場合、サイト側で検索を止められてしまうため、1件あたり10秒待つ。

import re
import argparse
import datetime
import time
import datetime
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
    select.select_by_value('DOM-HOLDER')  # 検索タイプを 'DOM-HOLDER' に設定

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

def process_pre_text(pre_text):
    processed_lines = []
    if pre_text.startswith("Domain Information: [ドメイン情報]"):
        return process_pre_text_cojp(pre_text)
    pre_text = re.sub(r'\n\s{40,}', ' ', pre_text)
    lines = pre_text.split('\n')

    for line in lines:
        # 括弧外のスペースをセミコロンで置き換える
        processed_line = re.sub(r'(\s+)(?![^()]*\))', ';', line)
        processed_lines.append(processed_line)
    return '\n'.join(processed_lines)

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
output_filename = f"output_searched_by_org_{current_time}.txt"

# Webドライバの設定
driver = webdriver.Chrome()

try:
    driver.get("https://whois.jprs.jp/")
    select_search_type(driver)

    with open(args.file_path, 'r', encoding='utf-8') as file, \
         open(output_filename, 'w', encoding='utf-8') as output_file:
        for keyword in file:
            keyword = keyword.strip()
            if keyword:
                enter_search_keyword(driver, keyword)

                try:
                    WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located((By.TAG_NAME, "pre"))
                    )
                    pre_text = driver.find_element(By.TAG_NAME, "pre").text
                    processed_text = process_pre_text(pre_text)
                    print(f"Results for '{keyword}':\n{processed_text}\n")
                    output_file.write(f"{processed_text}\n") 
                except TimeoutException:
                    print(f"検索キーワード '{keyword}' に該当するデータはありません。\n")
                    # output_file.write(f"検索キーワード '{keyword}' に該当するデータはありません。\n\n")

                # ここで10秒待機
                time.sleep(10)

finally:
    driver.quit()
