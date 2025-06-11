#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
script_01_generate_xlsx.py (v2.3 - Unified Excel Version)

基於統一的 phrase_comparison.xlsx 檔案生成各語言的 tobemodified_{language}.xlsx
支援多語言區塊統一管理，使用者在單一 Excel 中完成所有配置

功能：
1. 從統一的 phrase_comparison.xlsx 中讀取所有語言的敏感詞映射
2. 自動解析語言區塊結構
3. 為每個語言生成獨立的 tobemodified_{language}.xlsx
4. 支援統一的業態管理
"""

import json
import re
import itertools
import sys
import argparse
from pathlib import Path
from collections import defaultdict
from config_loader import get_config

try:
    import polib
    from openpyxl import Workbook
    import openpyxl
except ImportError as e:
    print(f"❌ 缺少必要套件：{e}")
    print("請執行：pip install polib openpyxl")
    sys.exit(1)


class UnifiedExcelMapping:
    """基於統一 Excel 檔案的映射類"""
    
    def __init__(self, config):
        """
        初始化統一 Excel 映射
        
        Args:
            config: 配置物件
        """
        self.config = config
        file_patterns = config.get_file_patterns()
        self.excel_path = Path(file_patterns.get('phrase_comparison', 'phrase_comparison.xlsx'))
        self.language_mappings = {}  # {language: {business_type: {keyword: replacement}}}
        self.language_categories = {}  # {language: {keyword: category}}
        self.load_unified_mappings()
    
    def load_unified_mappings(self):
        """從統一 Excel 檔案載入所有語言的映射關係"""
        if not self.excel_path.exists():
            print(f"❌ 找不到統一對照表：{self.excel_path}")
            print(f"請先執行：python generate_phrase_comparison.py")
            sys.exit(1)
        
        try:
            print(f"📖 載入統一對照表：{self.excel_path}")
            wb = openpyxl.load_workbook(self.excel_path, data_only=True)
            
            # 獲取主工作表
            excel_config = self.config.get_excel_config()
            comparison_sheet_name = excel_config.get('worksheets', {}).get('comparison', 'phrase_comparison')
            
            if comparison_sheet_name in wb.sheetnames:
                ws = wb[comparison_sheet_name]
            else:
                ws = wb.active
                print(f"⚠️  找不到工作表 '{comparison_sheet_name}'，使用預設工作表")
            
            self._parse_unified_excel(ws)
            
        except Exception as e:
            print(f"❌ 載入統一 Excel 檔案失敗：{e}")
            sys.exit(1)
    
    def _parse_unified_excel(self, ws):
        """解析統一 Excel 的結構"""
        # 讀取標題列（假設在第2行）
        header_row = 2
        headers = []
        for col in range(1, ws.max_column + 1):
            cell_value = ws.cell(row=header_row, column=col).value
            if cell_value:
                headers.append(str(cell_value).strip())
            else:
                headers.append("")
        
        # 建立欄位索引映射
        column_indices = {header: idx for idx, header in enumerate(headers) if header}
        
        print(f"   發現欄位：{list(column_indices.keys())}")
        
        # 檢查必要欄位
        excel_config = self.config.get_excel_config()
        required_columns = excel_config.get('required_columns', {})
        
        language_col = required_columns.get('language', '語言')
        category_col = required_columns.get('category', '敏感詞類型')
        keyword_col = required_columns.get('keyword', '敏感詞')
        
        missing_columns = []
        for col_name in [language_col, category_col, keyword_col]:
            if col_name not in column_indices:
                missing_columns.append(col_name)
        
        # 檢查業態欄位
        business_types = self.config.get_business_types()
        business_columns = excel_config.get('business_columns', {})
        solution_template = business_columns.get('solution_template', '對應方案({display_name})')
        
        business_column_indices = {}
        for bt_code, bt_config in business_types.items():
            display_name = bt_config['display_name']
            solution_col = solution_template.format(display_name=display_name)
            if solution_col not in column_indices:
                missing_columns.append(solution_col)
            else:
                business_column_indices[bt_code] = column_indices[solution_col]
        
        if missing_columns:
            print(f"❌ Excel 缺少必要欄位：{missing_columns}")
            print(f"現有欄位：{list(column_indices.keys())}")
            sys.exit(1)
        
        # 初始化語言映射
        detected_languages = set()
        
        # 讀取資料行（從第3行開始）
        current_language = None
        row_count = 0
        
        for row_num in range(3, ws.max_row + 1):
            row_values = []
            for col in range(1, len(headers) + 1):
                cell = ws.cell(row=row_num, column=col)
                row_values.append(cell.value)
            
            # 安全讀取欄位值
            def get_cell_value(col_name):
                if col_name in column_indices:
                    idx = column_indices[col_name]
                    if idx < len(row_values) and row_values[idx] is not None:
                        return str(row_values[idx]).strip()
                return ""
            
            language = get_cell_value(language_col)
            category = get_cell_value(category_col)
            keyword = get_cell_value(keyword_col)
            
            # 更新當前語言
            if language:
                current_language = language
                detected_languages.add(language)
                if language not in self.language_mappings:
                    self.language_mappings[language] = {}
                    for bt_code in business_types.keys():
                        self.language_mappings[language][bt_code] = {}
                if language not in self.language_categories:
                    self.language_categories[language] = {}
            
            # 處理敏感詞
            if current_language and keyword:
                # 記錄分類
                if category:
                    self.language_categories[current_language][keyword] = category
                
                # 讀取各業態的對應方案
                for bt_code in business_types.keys():
                    if bt_code in business_column_indices:
                        col_idx = business_column_indices[bt_code]
                        if col_idx < len(row_values):
                            solution = row_values[col_idx]
                            if solution is not None:
                                solution = str(solution).strip()
                            else:
                                solution = ""
                        else:
                            solution = ""
                        
                        # 如果沒有方案，使用原敏感詞
                        if not solution:
                            solution = keyword
                        
                        self.language_mappings[current_language][bt_code][keyword] = solution
                
                row_count += 1
        
        print(f"✅ 成功載入 {len(detected_languages)} 個語言，{row_count} 個敏感詞映射")
        
        # 顯示載入統計
        for language in detected_languages:
            if language in self.language_mappings:
                total_keywords = len(self.language_categories.get(language, {}))
                print(f"   {language}: {total_keywords} 個敏感詞")
                
                for bt_code, bt_config in business_types.items():
                    display_name = bt_config['display_name']
                    mapping = self.language_mappings[language].get(bt_code, {})
                    replaced_count = sum(1 for k, v in mapping.items() if k != v)
                    print(f"     {display_name}: {replaced_count} 個有替換方案")
    
    def get_language_keywords(self, language: str) -> set:
        """獲取指定語言的所有敏感詞"""
        if language not in self.language_categories:
            return set()
        return set(self.language_categories[language].keys())
    
    def get_language_categories(self, language: str) -> dict:
        """獲取指定語言的敏感詞分類映射"""
        return self.language_categories.get(language, {})
    
    def get_replacement(self, language: str, keyword: str, business_type_code: str) -> str:
        """獲取指定語言和業態下的敏感詞替換方案"""
        if language not in self.language_mappings:
            return keyword
        
        mapping = self.language_mappings[language].get(business_type_code, {})
        return mapping.get(keyword, keyword)
    
    def apply_replacements(self, language: str, text: str, business_type_code: str) -> str:
        """對文本應用指定語言和業態的敏感詞替換"""
        if not text or language not in self.language_mappings:
            return text
        
        mapping = self.language_mappings[language].get(business_type_code, {})
        result = text
        
        # 按長度排序，優先替換長詞
        sorted_keywords = sorted(mapping.keys(), key=len, reverse=True)
        
        for keyword in sorted_keywords:
            replacement = mapping[keyword]
            if keyword != replacement:
                result = result.replace(keyword, replacement)
        
        return result
    
    def build_replacement_plan(self, language: str, keywords: list, business_type_code: str) -> str:
        """建立指定語言和業態的替換方案說明"""
        if language not in self.language_mappings:
            return ""
        
        mapping = self.language_mappings[language].get(business_type_code, {})
        replacements = []
        
        for keyword in keywords:
            replacement = mapping.get(keyword, keyword)
            if replacement != keyword:
                replacements.append(f"{keyword}→{replacement}")
        
        return "、".join(replacements)
    
    def get_available_languages(self) -> list:
        """獲取統一 Excel 中可用的語言列表"""
        return list(self.language_mappings.keys())


def main():
    """主執行函數"""
    print("🚀 開始基於統一 Excel 生成各語言 tobemodified 檔案")
    
    # 載入配置
    config = get_config()
    config.print_config_summary()
    
    # 處理命令列參數
    parser = argparse.ArgumentParser(description='基於統一 Excel 生成敏感詞檢測結果')
    parser.add_argument('--language', '-l', 
                       help='指定要處理的語言（若未指定將處理所有可用語言）')
    parser.add_argument('--list-languages', action='store_true',
                       help='列出統一 Excel 中的所有語言')
    
    args = parser.parse_args()
    
    # 載入統一 Excel 映射
    try:
        unified_mapper = UnifiedExcelMapping(config)
    except Exception as e:
        print(f"❌ 載入統一 Excel 失敗：{e}")
        return False
    
    # 獲取可用語言
    excel_languages = unified_mapper.get_available_languages()
    input_languages = config.detect_available_languages()
    
    if args.list_languages:
        print(f"\n🌐 統一 Excel 中的語言：")
        for lang in excel_languages:
            status = "✅ 有輸入檔案" if lang in input_languages else "❌ 缺少輸入檔案"
            keywords_count = len(unified_mapper.get_language_keywords(lang))
            print(f"   {lang}: {keywords_count} 個敏感詞 - {status}")
        return True
    
    # 選擇要處理的語言
    if args.language:
        if args.language not in excel_languages:
            print(f"❌ 語言 '{args.language}' 不在統一 Excel 中：{excel_languages}")
            sys.exit(1)
        if args.language not in input_languages:
            print(f"❌ 語言 '{args.language}' 缺少輸入檔案")
            sys.exit(1)
        target_languages = [args.language]
        print(f"\n🌐 將處理指定語言：{args.language}")
    else:
        # 取交集：既在 Excel 中又有輸入檔案的語言
        target_languages = list(set(excel_languages) & set(input_languages))
        if not target_languages:
            print(f"❌ 沒有語言同時存在於統一 Excel 和輸入檔案中")
            print(f"   Excel 中的語言：{excel_languages}")
            print(f"   輸入檔案語言：{input_languages}")
            sys.exit(1)
        print(f"\n🌐 將處理所有可用語言：{', '.join(target_languages)}")
    
    # 處理每個語言
    success_count = 0
    for language in target_languages:
        print(f"\n{'='*60}")
        print(f"📋 處理語言：{language}")
        
        if process_language(config, unified_mapper, language):
            success_count += 1
        else:
            print(f"❌ {language} 處理失敗")
    
    print(f"\n🎉 處理完成！成功：{success_count}/{len(target_languages)} 個語言")
    return success_count == len(target_languages)


def process_language(config, unified_mapper: UnifiedExcelMapping, language: str) -> bool:
    """
    處理單個語言的 tobemodified 生成
    
    Args:
        config: 配置物件
        unified_mapper: 統一 Excel 映射物件
        language: 語言代碼
    
    Returns:
        是否成功
    """
    
    # 獲取檔案路徑
    language_files = config.get_language_files(language)
    file_patterns = config.get_file_patterns()
    tobemodified_template = file_patterns.get('tobemodified', 'tobemodified_{language}.xlsx')
    tobemodified_path = Path(tobemodified_template.format(language=language))
    
    print(f"   來源檔案：{list(language_files.values())}")
    print(f"   輸出檔案：{tobemodified_path}")
    
    # 獲取該語言的敏感詞
    all_keywords = unified_mapper.get_language_keywords(language)
    language_categories = unified_mapper.get_language_categories(language)
    
    print(f"   敏感詞數量：{len(all_keywords)}")
    
    if not all_keywords:
        print(f"⚠️  {language} 沒有敏感詞，跳過處理")
        return True
    
    # 建立關鍵字檢測器
    detection_config = config.get_keyword_detection_config()
    priority_by_length = detection_config.get('priority_by_length', True)
    
    if priority_by_length:
        sorted_keywords = sorted(all_keywords, key=len, reverse=True)
    else:
        sorted_keywords = sorted(all_keywords)
    
    KW_RE = re.compile("|".join(map(re.escape, sorted_keywords)))
    
    def find_keywords(text: str) -> list[str]:
        """在文本中找到所有敏感詞，避免重複"""
        if not text:
            return []
        
        seen = set()
        keywords = []
        for match in KW_RE.finditer(text):
            word = match.group(0)
            if word not in seen:
                seen.add(word)
                keywords.append(word)
        return keywords
    
    # 檔案讀取函數
    def iter_po_entries():
        """迭代 PO 檔案條目"""
        if 'po_file' not in language_files:
            return
        
        po_path = language_files['po_file']
        try:
            po_file = polib.pofile(str(po_path))
            count = 0
            for entry in po_file:
                msgid = entry.msgid or ""
                msgstr = entry.msgstr or ""
                yield ("po", msgid, msgstr)
                count += 1
            print(f"   PO 檔案: {count} 個條目")
        except Exception as e:
            print(f"❌ 讀取 PO 檔案失敗：{e}")
    
    def iter_json_entries():
        """迭代 JSON 檔案條目"""
        if 'json_file' not in language_files:
            return
        
        json_path = language_files['json_file']
        try:
            data = json.loads(json_path.read_text("utf-8"))
            
            def walk_json(node, path=""):
                """遞迴遍歷 JSON 結構"""
                if isinstance(node, dict):
                    for key, value in node.items():
                        new_path = f"{path}.{key}" if path else key
                        yield from walk_json(value, new_path)
                elif isinstance(node, list):
                    for index, value in enumerate(node):
                        new_path = f"{path}[{index}]"
                        yield from walk_json(value, new_path)
                else:
                    yield ("json", path, str(node))
            
            count = 0
            for entry in walk_json(data):
                yield entry
                count += 1
            print(f"   JSON 檔案: {count} 個條目")
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON 格式錯誤：{e}")
        except Exception as e:
            print(f"❌ 讀取 JSON 檔案失敗：{e}")
    
    # 掃描檔案並收集資料
    print(f"📖 掃描 {language} 檔案...")
    rows = []
    detection_stats = defaultdict(int)
    
    for source, key, value in itertools.chain(iter_po_entries(), iter_json_entries()):
        # 如果 value 為空，使用 key
        display_value = value if value else key
        
        # 檢測 key 和 value 中的敏感詞
        key_keywords = find_keywords(key)
        value_keywords = find_keywords(display_value)
        
        # 合併關鍵字，避免重複
        all_keywords_found = key_keywords + [kw for kw in value_keywords if kw not in key_keywords]
        
        if all_keywords_found:
            detection_stats[source] += 1
            detection_stats['total_entries'] += 1
            
            # 使用統一 Excel 映射建立修正方案和結果
            row_data = [
                source,
                key,
                display_value,
                "、".join(all_keywords_found),  # 敏感詞列表
            ]
            
            # 添加各業態的修正方案和結果
            business_types = config.get_business_types()
            for bt_code, bt_config in business_types.items():
                row_data.extend([
                    unified_mapper.build_replacement_plan(language, all_keywords_found, bt_code),  # 修正方案
                    unified_mapper.apply_replacements(language, display_value, bt_code),           # 修正結果
                ])
            
            rows.append(row_data)
    
    print(f"   檢測統計：{dict(detection_stats)}")
    
    if not rows:
        print(f"✅ {language} 未偵測到歧義詞，未產生 Excel")
        return True
    
    # 輸出 Excel
    print(f"📝 生成 {language} Excel 檔案...")
    
    try:
        wb = Workbook()
        ws = wb.active
        ws.title = f"tobemodified_{language}"
        
        # 動態建立標題列
        headers = ["source", "key", "value", "敏感詞"]
        
        business_types = config.get_business_types()
        for bt_code, bt_config in business_types.items():
            display_name = bt_config['display_name']
            headers.extend([
                f"修正方案({display_name})",
                f"修正結果({display_name})"
            ])
        
        ws.append(headers)
        print(f"   Excel 標題列: {headers}")
        
        # 資料列
        for row in rows:
            ws.append(row)
        
        # 自動調整欄寬
        for col in ws.columns:
            max_length = 0
            column_letter = col[0].column_letter
            
            for cell in col:
                try:
                    cell_length = len(str(cell.value or ""))
                    if cell_length > max_length:
                        max_length = cell_length
                except:
                    pass
            
            # 設定欄寬，最小10，最大80
            adjusted_width = min(max(max_length + 4, 10), 80)
            ws.column_dimensions[column_letter].width = adjusted_width
        
        # 確保輸出目錄存在
        tobemodified_path.parent.mkdir(parents=True, exist_ok=True)
        wb.save(tobemodified_path)
        
        print(f"✅ 已輸出 {tobemodified_path.resolve()}")
        print(f"📄 檔案大小：{tobemodified_path.stat().st_size / 1024:.1f} KB")
        print(f"📊 總共處理：{len(rows)} 個包含敏感詞的條目")
        
        # 生成統計報告
        if language_categories:
            category_detections = defaultdict(int)
            keyword_detections = defaultdict(int)
            
            for row in rows:
                keywords = row[3].split("、") if row[3] else []
                for kw in keywords:
                    if kw in language_categories:
                        category_detections[language_categories[kw]] += 1
                        keyword_detections[kw] += 1
            
            if category_detections:
                print(f"   最常出現的分類：")
                for cat, count in sorted(category_detections.items(), key=lambda x: x[1], reverse=True)[:3]:
                    print(f"     {cat}: {count} 次")
            
            if keyword_detections:
                print(f"   最常出現的敏感詞：")
                for kw, count in sorted(keyword_detections.items(), key=lambda x: x[1], reverse=True)[:3]:
                    print(f"     {kw}: {count} 次")
        
        return True
        
    except Exception as e:
        print(f"❌ 生成 Excel 檔案失敗：{e}")
        return False


if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)