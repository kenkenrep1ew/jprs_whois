# jprs_whois_search_by_org.pyで使う検索キーワードを生成するようのスクリプト。
# 実行は必須ではない。
# 
# kw_pairs_{current_time}.txtを出力する。

import sys
import datetime

def generate_combinations(keyword1, keyword2):
    combinations = []

    # スペースなしのパターンを生成
    combination1 = keyword1 + keyword2
    combinations.append(combination1)

    # 半角スペースを追加したパターンを生成
    combination2 = keyword1 + " " + keyword2
    combinations.append(combination2)

    # 全角スペースを追加したパターンを生成
    combination3 = keyword1 + "　" + keyword2  # 全角スペースを使用
    combinations.append(combination3)

    # キーワードの順序を入れ替えた組み合わせを生成
    # スペースなしのパターンを生成
    combination4 = keyword2 + keyword1
    combinations.append(combination4)

    # 半角スペースを追加したパターンを生成
    combination5 = keyword2 + " " + keyword1
    combinations.append(combination5)

    # 全角スペースを追加したパターンを生成
    combination6 = keyword2 + "　" + keyword1  # 全角スペースを使用
    combinations.append(combination6)

    return combinations

# ファイルからキーワードの組み合わせを読み取る関数
def read_keyword_pairs_from_file(filename):
    keyword_pairs = []
    with open(filename, 'r') as file:
        lines = file.readlines()
        for line in lines:
            keywords = line.strip().split(',')
            if len(keywords) == 2:
                keyword_pairs.append((keywords[0], keywords[1]))
    return keyword_pairs



# メインプログラム
if __name__ == "__main__":
    current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"kw_pairs_{current_time}.txt"
    if len(sys.argv) != 2:
        print("ファイル名を指定してください。")
    else:
        filename = sys.argv[1]
        keyword_pairs = read_keyword_pairs_from_file(filename)
        with open(output_filename, 'w', encoding='utf-8') as output_file:
            # 各組み合わせに対して処理を行い、結果を出力
            for keyword1, keyword2 in keyword_pairs:
                combinations = generate_combinations(keyword1, keyword2)
                print(f"キーワード1: {keyword1}, キーワード2: {keyword2}")
                for combination in combinations:
                    print(combination)
                    output_file.write(f"{combination}\n")
                print()
