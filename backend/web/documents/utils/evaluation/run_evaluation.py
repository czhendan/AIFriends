import os
import sys

# 确保 Django 环境已加载
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
import django
django.setup()

from web.documents.utils.evaluation.generate_dataset import generate_dataset
from web.documents.utils.evaluation.evaluator import load_dataset, evaluate, print_report


def run():
    dataset_path = os.path.join(os.path.dirname(__file__), "test_dataset.json")

    # Step 1: 生成测试集（如果已存在则跳过）
    if not os.path.exists(dataset_path):
        print("=== Step 1: 生成测试数据集 ===")
        generate_dataset(dataset_path)
    else:
        print(f"=== Step 1: 测试数据集已存在，跳过生成 ({dataset_path}) ===")

    # Step 2: 载入测试集
    print("\n=== Step 2: 载入测试数据集 ===")
    queries = load_dataset(dataset_path)
    print(f"共 {len(queries)} 条测试查询")

    # Step 3: 三路评估
    print("\n=== Step 3: 执行三路检索评估 ===")
    ks = [3, 5, 10]
    results = evaluate(queries, ks=ks)

    # Step 4: 输出对比报告
    print("\n=== Step 4: 评估对比报告 ===\n")
    print_report(results, ks=ks)


if __name__ == "__main__":
    run()
