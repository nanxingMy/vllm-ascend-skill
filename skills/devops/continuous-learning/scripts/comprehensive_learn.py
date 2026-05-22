#!/usr/bin/env python3
"""
每天凌晨全面学习 vllm-ascend 项目

学习维度：
1. 代码结构分析
2. 关键类和方法
3. 测试用例学习
4. 文档和注释
5. 最佳实践提取
6. 性能优化技巧
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# 配置
VLLM_ASCEND_DIR = Path("C:/Users/HuaWei/vllm-ascend")
SKILL_DIR = Path("C:/Users/HuaWei/vllm-ascend-skill/skill/references")
GIT_USER = "nanxingMy"
GIT_EMAIL = "1014662416@qq.com"

class VLLMAscendLearner:
    """vLLM-Ascend 学习器"""
    
    def __init__(self):
        self.knowledge = {
            "structure": {},
            "classes": [],
            "methods": [],
            "tests": [],
            "patterns": [],
            "best_practices": []
        }
    
    def learn_structure(self):
        """学习项目结构"""
        print("学习项目结构...")
        
        # 关键目录
        key_dirs = {
            "core": "vllm_ascend",
            "worker": "vllm_ascend/worker",
            "platform": "vllm_ascend/platform",
            "attention": "vllm_ascend/attention",
            "ops": "vllm_ascend/ops",
            "distributed": "vllm_ascend/distributed",
            "patch": "vllm_ascend/patch",
            "quantization": "vllm_ascend/quantization",
            "tests": "tests",
            "docs": "docs"
        }
        
        for name, path in key_dirs.items():
            dir_path = VLLM_ASCEND_DIR / path
            if dir_path.exists():
                py_files = list(dir_path.glob("*.py"))
                
                self.knowledge["structure"][name] = {
                    "path": path,
                    "file_count": len(py_files),
                    "total_lines": sum(
                        len(f.read_text(encoding='utf-8', errors='ignore').split('\n'))
                        for f in py_files[:20]
                        if f.exists()
                    )
                }
    
    def learn_classes(self):
        """学习关键类"""
        print("学习关键类...")
        
        key_files = [
            "vllm_ascend/platform.py",
            "vllm_ascend/worker/worker.py",
            "vllm_ascend/ascend_config.py",
            "vllm_ascend/utils.py"
        ]
        
        for file_path in key_files:
            full_path = VLLM_ASCEND_DIR / file_path
            if full_path.exists():
                content = full_path.read_text(encoding='utf-8', errors='ignore')
                
                # 提取类定义
                class_pattern = r'class (\w+)(?:\(([^)]+)\))?:\s*"""([^"]*)"""'
                for match in re.finditer(class_pattern, content, re.DOTALL):
                    class_name = match.group(1)
                    base_class = match.group(2) or "object"
                    docstring = match.group(3).strip()
                    
                    self.knowledge["classes"].append({
                        "name": class_name,
                        "file": file_path,
                        "base": base_class,
                        "doc": docstring[:200]  # 限制长度
                    })
    
    def learn_methods(self):
        """学习关键方法"""
        print("学习关键方法...")
        
        key_files = [
            "vllm_ascend/platform.py",
            "vllm_ascend/worker/worker.py"
        ]
        
        for file_path in key_files:
            full_path = VLLM_ASCEND_DIR / file_path
            if full_path.exists():
                content = full_path.read_text(encoding='utf-8', errors='ignore')
                
                # 提取方法定义
                method_pattern = r'def (\w+)\(([^)]*)\)(?:\s*->\s*([^:]+))?:\s*"""([^"]*)"""'
                for match in re.finditer(method_pattern, content, re.DOTALL):
                    method_name = match.group(1)
                    params = match.group(2)
                    return_type = match.group(3) or "None"
                    docstring = match.group(4).strip()
                    
                    # 过滤特殊方法
                    if not method_name.startswith('_'):
                        self.knowledge["methods"].append({
                            "name": method_name,
                            "file": file_path,
                            "params": params[:100],
                            "return": return_type.strip(),
                            "doc": docstring[:200]
                        })
    
    def learn_tests(self):
        """学习测试用例"""
        print("学习测试用例...")
        
        test_dirs = [
            "tests/ut",
            "tests/e2e"
        ]
        
        for test_dir in test_dirs:
            dir_path = VLLM_ASCEND_DIR / test_dir
            if dir_path.exists():
                test_files = list(dir_path.glob("**/test_*.py"))
                
                for test_file in test_files[:20]:  # 限制数量
                    try:
                        content = test_file.read_text(encoding='utf-8', errors='ignore')
                        
                        # 提取测试函数
                        test_pattern = r'def (test_\w+)\('
                        test_names = re.findall(test_pattern, content)
                        
                        if test_names:
                            self.knowledge["tests"].append({
                                "file": str(test_file.relative_to(VLLM_ASCEND_DIR)),
                                "test_count": len(test_names),
                                "tests": test_names[:10]
                            })
                    except:
                        pass
    
    def learn_patterns(self):
        """学习设计模式"""
        print("学习设计模式...")
        
        patterns_found = defaultdict(list)
        
        # 设计模式特征
        pattern_checks = {
            "Singleton": [r'_instance\s*=\s*None', r'get_instance\('],
            "Factory": [r'def create_\w+', r'class \w+Factory'],
            "Strategy": [r'class \w+Strategy', r'strategy\s*='],
            "Adapter": [r'class \w+Adapter', r'adapt\('],
            "Decorator": [r'def wrapper\(', r'@'],
            "Observer": [r'add_observer\(', r'notify\('],
        }
        
        for py_file in VLLM_ASCEND_DIR.glob("vllm_ascend/**/*.py"):
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                
                for pattern_name, patterns in pattern_checks.items():
                    for pattern in patterns:
                        if re.search(pattern, content):
                            patterns_found[pattern_name].append(
                                str(py_file.relative_to(VLLM_ASCEND_DIR))
                            )
                            break
            except:
                pass
        
        for pattern_name, files in patterns_found.items():
            self.knowledge["patterns"].append({
                "pattern": pattern_name,
                "files": files[:5]  # 限制数量
            })
    
    def extract_best_practices(self):
        """提取最佳实践"""
        print("提取最佳实践...")
        
        best_practices = []
        
        # 检查代码质量特征
        quality_checks = [
            ("类型注解", r'def \w+\([^)]*\)\s*->'),
            ("文档字符串", r'"""[^"]*"""'),
            ("错误处理", r'raise \w+Error'),
            ("日志记录", r'logger\.\w+\('),
            ("上下文管理", r'with\s+'),
        ]
        
        for py_file in VLLM_ASCEND_DIR.glob("vllm_ascend/**/*.py"):
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                
                for practice_name, pattern in quality_checks:
                    matches = re.findall(pattern, content)
                    if len(matches) > 5:  # 至少5次使用
                        best_practices.append({
                            "practice": practice_name,
                            "file": str(py_file.relative_to(VLLM_ASCEND_DIR)),
                            "count": len(matches)
                        })
            except:
                pass
        
        # 按使用次数排序
        best_practices.sort(key=lambda x: x["count"], reverse=True)
        self.knowledge["best_practices"] = best_practices[:20]
    
    def generate_report(self):
        """生成学习报告"""
        print("生成学习报告...")
        
        report_file = SKILL_DIR / "deep-learning-report.md"
        
        content = f"""# vLLM-Ascend 深度学习报告

> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 项目结构

"""
        
        for name, info in self.knowledge["structure"].items():
            content += f"### {name.upper()}\n\n"
            content += f"- 路径: `{info['path']}`\n"
            content += f"- 文件数: {info['file_count']}\n"
            content += f"- 总行数: {info['total_lines']:,}\n\n"
        
        content += "\n## 🏗️ 关键类\n\n"
        
        for cls in self.knowledge["classes"][:20]:
            content += f"### {cls['name']}\n\n"
            content += f"- 文件: `{cls['file']}`\n"
            content += f"- 基类: `{cls['base']}`\n"
            if cls['doc']:
                content += f"- 说明: {cls['doc']}\n"
            content += "\n"
        
        content += "\n## 🔧 关键方法\n\n"
        
        for method in self.knowledge["methods"][:30]:
            content += f"### {method['name']}\n\n"
            content += f"- 文件: `{method['file']}`\n"
            content += f"- 参数: `{method['params']}`\n"
            content += f"- 返回: `{method['return']}`\n"
            if method['doc']:
                content += f"- 说明: {method['doc']}\n"
            content += "\n"
        
        content += "\n## 🧪 测试覆盖\n\n"
        
        for test in self.knowledge["tests"][:10]:
            content += f"### {test['file']}\n\n"
            content += f"- 测试数: {test['test_count']}\n"
            content += f"- 测试: {', '.join(test['tests'][:5])}\n\n"
        
        content += "\n## 🎨 设计模式\n\n"
        
        for pattern in self.knowledge["patterns"]:
            content += f"### {pattern['pattern']}\n\n"
            content += f"- 文件: {', '.join(pattern['files'])}\n\n"
        
        content += "\n## ✨ 最佳实践\n\n"
        
        for practice in self.knowledge["best_practices"][:10]:
            content += f"- **{practice['practice']}**: {practice['count']} 次 ({practice['file']})\n"
        
        # 写入文件
        report_file.write_text(content, encoding='utf-8')
    
    def save_knowledge(self):
        """保存知识到 JSON"""
        knowledge_file = SKILL_DIR / "knowledge.json"
        
        with open(knowledge_file, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge, f, indent=2, ensure_ascii=False)
    
    def git_commit_and_push(self):
        """提交并推送"""
        import subprocess
        
        os.chdir(SKILL_DIR.parent.parent)
        
        subprocess.run(['git', 'config', 'user.name', GIT_USER], check=True)
        subprocess.run(['git', 'config', 'user.email', GIT_EMAIL], check=True)
        subprocess.run(['git', 'add', 'skill/references/'], check=True)
        
        commit_msg = f"[Auto] Deep learn vllm-ascend - {datetime.now().strftime('%Y-%m-%d')}"
        subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)
    
    def learn(self):
        """执行学习"""
        print(f"\n{'='*60}")
        print(f"开始深度学习 vllm-ascend - {datetime.now()}")
        print(f"{'='*60}\n")
        
        self.learn_structure()
        self.learn_classes()
        self.learn_methods()
        self.learn_tests()
        self.learn_patterns()
        self.extract_best_practices()
        
        self.generate_report()
        self.save_knowledge()
        
        print("\n提交并推送...")
        self.git_commit_and_push()
        
        print(f"\n{'='*60}")
        print("学习完成！")
        print(f"{'='*60}\n")

if __name__ == "__main__":
    learner = VLLMAscendLearner()
    learner.learn()
