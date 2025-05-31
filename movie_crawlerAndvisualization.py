#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
豆瓣电影数据爬虫与可视化分析

本脚本专门用于爬取豆瓣电影Top250数据，并进行可视化分析，
包括箱线图、小提琴图、散点图等多种图表类型。
"""

# 基础库
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import time
import random
import re
import os

# 数据可视化库
import matplotlib.pyplot as plt
import seaborn as sns

# 中文字体设置
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# 设置随机种子
np.random.seed(42)
random.seed(42)

# 创建文件保存目录
if not os.path.exists('results'):
    os.makedirs('results')
    print("创建results文件夹")

print("所有库导入成功！")


class DoubanMovieScraper:
    """豆瓣电影爬虫"""
    
    def __init__(self):
        self.movies = []
    
    def request_douban(self, url):
        """发送请求获取页面内容"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/88.0.4324.146 Safari/537.36',
        }

        try:
            response = requests.get(url=url, headers=headers)
            if response.status_code == 200:
                return response.text
        except requests.RequestException as e:
            print(f"请求出错: {e}")
            return None

    def parse_movies(self, soup):
        """解析电影信息"""
        movies = []
        movie_list = soup.find(class_='grid_view')
        if not movie_list:
            return movies
            
        movie_items = movie_list.find_all('div', class_='item')

        for item in movie_items:
            try:
                # 电影名称
                title_element = item.find(class_='title')
                if not title_element:
                    continue
                item_name = title_element.string
                
                # 图片
                img_element = item.find('img')
                if not img_element:
                    continue
                item_img = img_element.get('src')
                
                # 排名
                rank_element = item.find(class_='pic').find('em')
                if not rank_element:
                    continue
                item_index = rank_element.string
                
                # 评分
                rating_element = item.find(class_='rating_num')
                if not rating_element:
                    continue
                item_score = float(rating_element.string)
                
                # 导演和演员信息
                author_element = item.find('p')
                if not author_element:
                    continue
                item_author = author_element.text.strip()
                
                # 简介
                inq_element = item.find(class_='inq')
                item_intr = inq_element.string if inq_element else 'NOT AVAILABLE'

                print('爬取电影：' + item_index + ' | ' + item_name + ' | ' + str(item_score) + ' | ' + item_intr)

                movie_data = {
                    '名称': item_name,
                    '图片': item_img,
                    '排名': int(item_index),
                    '评分': item_score,
                    '作者信息': item_author,
                    '简介': item_intr
                }
                
                movies.append(movie_data)
            except Exception as e:
                print(f"解析电影信息出错: {e}")
                continue
        
        return movies

    def scrape_movies(self, max_pages=10):
        """爬取电影数据"""
        print(f"开始爬取豆瓣电影Top250数据，共{max_pages}页...")
        
        for i in range(max_pages):
            url = 'https://movie.douban.com/top250?start=' + str(i * 25) + '&filter='
            print(f'正在爬取第{i+1}页数据...')
            
            html = self.request_douban(url)
            if html:
                soup = BeautifulSoup(html, 'lxml')
                movies = self.parse_movies(soup)
                self.movies.extend(movies)
                print(f'第{i+1}页获取到{len(movies)}部电影')
            else:
                print(f'第{i+1}页爬取失败')
            
            # 延时避免被反爬
            time.sleep(random.uniform(2, 4))
        
        print(f'电影数据爬取完成！总共获取到{len(self.movies)}部电影')
        return self.movies

    def save_to_excel(self, filename='results/movies_data.xlsx'):
        """保存数据到Excel文件"""
        if self.movies:
            # 转换为DataFrame
            df = pd.DataFrame(self.movies)
            
            # 保存到Excel
            try:
                df.to_excel(filename, index=False, engine='openpyxl')
                print(f"电影数据已保存到Excel文件: {filename}")
            except Exception as e:
                print(f"保存Excel文件时出错: {e}")
                print("提示：如果出现错误，请安装openpyxl库：pip install openpyxl")
        else:
            print("没有数据可保存")


def process_movie_data(movies_df):
    """电影数据清洗与处理"""
    print("=== 电影数据处理 ===")
    if movies_df.empty:
        print("电影数据为空，可能爬取失败")
        return movies_df
    
    print(f"电影数据形状: {movies_df.shape}")
    print(f"\n电影数据类型:")
    print(movies_df.dtypes)
    print(f"\n缺失值统计:")
    print(movies_df.isnull().sum())
    
    # 评分分组
    if '评分' in movies_df.columns and movies_df['评分'].dtype in ['float64', 'int64']:
        def categorize_rating(rating):
            if rating >= 9.0:
                return '经典(≥9.0)'
            elif rating >= 8.5:
                return '优秀(8.5-9.0)'
            elif rating >= 8.0:
                return '良好(8.0-8.5)'
            else:
                return '一般(<8.0)'
        
        movies_df['评分等级'] = movies_df['评分'].apply(categorize_rating)
    
    print("\n电影数据描述性统计:")
    print(movies_df.describe())
    
    return movies_df


def visualize_movies_data(movies_df):
    """电影数据可视化"""
    if movies_df.empty:
        print("电影数据为空，无法进行可视化")
        return
    
    # 1. 电影评分分布箱线图
    if '评分' in movies_df.columns:
        plt.figure(figsize=(8, 6))
        sns.boxplot(y=movies_df['评分'])
        plt.title('电影评分分布（箱线图）', fontsize=14, fontweight='bold')
        plt.ylabel('评分')
        plt.tight_layout()
        plt.savefig('results/movies_rating_boxplot.png', dpi=300, bbox_inches='tight')
        print("电影评分分布箱线图已保存到: results/movies_rating_boxplot.png")
        plt.show()

    # 2. 电影评分分布小提琴图
    if '评分' in movies_df.columns:
        plt.figure(figsize=(8, 6))
        sns.violinplot(y=movies_df['评分'])
        plt.title('电影评分分布（小提琴图）', fontsize=14, fontweight='bold')
        plt.ylabel('评分')
        plt.tight_layout()
        plt.savefig('results/movies_rating_violin.png', dpi=300, bbox_inches='tight')
        print("电影评分分布小提琴图已保存到: results/movies_rating_violin.png")
        plt.show()

    # 3. 不同评分等级的电影数量
    if '评分等级' in movies_df.columns:
        plt.figure(figsize=(10, 6))
        rating_counts = movies_df['评分等级'].value_counts()
        
        # 为每个评分等级设置不同颜色
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
        plt.bar(rating_counts.index, rating_counts.values, color=colors[:len(rating_counts)])
        
        plt.title('不同评分等级的电影数量', fontsize=14, fontweight='bold')
        plt.ylabel('数量')
        plt.xlabel('评分等级')
        plt.xticks(rotation=45)
        
        # 添加数值标签
        for i, v in enumerate(rating_counts.values):
            plt.text(i, v + 1, str(v), ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('results/movies_rating_levels.png', dpi=300, bbox_inches='tight')
        print("评分等级分布图已保存到: results/movies_rating_levels.png")
        plt.show()

    # 4. 电影排名分布
    if '排名' in movies_df.columns:
        plt.figure(figsize=(8, 6))
        
        # 创建彩色直方图
        n, bins, patches = plt.hist(movies_df['排名'], bins=20, alpha=0.8, edgecolor='black')
        
        # 为每个柱子设置不同颜色（渐变效果）
        colors = plt.cm.viridis(np.linspace(0, 1, len(patches)))
        for patch, color in zip(patches, colors):
            patch.set_facecolor(color)
        
        plt.title('电影排名分布', fontsize=14, fontweight='bold')
        plt.xlabel('排名')
        plt.ylabel('频次')
        plt.tight_layout()
        plt.savefig('results/movies_rank_distribution.png', dpi=300, bbox_inches='tight')
        print("电影排名分布图已保存到: results/movies_rank_distribution.png")
        plt.show()
    
    # 打印电影统计信息
    print("=== 电影数据统计信息 ===")
    if '评分' in movies_df.columns:
        print(f"平均评分: {movies_df['评分'].mean():.2f}")
        print(f"评分中位数: {movies_df['评分'].median():.2f}")
        print(f"评分标准差: {movies_df['评分'].std():.2f}")
    
    if '评分等级' in movies_df.columns:
        print("\n评分等级统计:")
        print(movies_df['评分等级'].value_counts())


def compare_visualizations(movies_df):
    """箱线图与小提琴图对比分析"""
    if movies_df.empty or '评分' not in movies_df.columns:
        print("电影数据不足，无法进行对比可视化")
        return
    
    # 创建箱线图
    plt.figure(figsize=(8, 6))
    sns.boxplot(y=movies_df['评分'])
    plt.title('电影评分分布 - 箱线图', fontsize=14, fontweight='bold')
    plt.ylabel('评分')
    plt.tight_layout()
    
    # 保存箱线图
    plt.savefig('results/movies_boxplot.png', dpi=300, bbox_inches='tight')
    print("电影评分箱线图已保存到: results/movies_boxplot.png")
    plt.show()
    
    # 创建小提琴图
    plt.figure(figsize=(8, 6))
    sns.violinplot(y=movies_df['评分'], inner='box')
    plt.title('电影评分分布 - 小提琴图', fontsize=14, fontweight='bold')
    plt.ylabel('评分')
    plt.tight_layout()
    
    # 保存小提琴图
    plt.savefig('results/movies_violin.png', dpi=300, bbox_inches='tight')
    print("电影评分小提琴图已保存到: results/movies_violin.png")
    plt.show()

    # 分析说明
    print("=== 箱线图和小提琴图分析说明 ===")
    print("\n箱线图特点:")
    print("- 清晰显示四分位数（Q1, Q2, Q3）")
    print("- 明确标识异常值（outliers）")
    print("- 适合快速了解数据的集中趋势和离散程度")
    print("- 占用空间小，适合多组数据对比")

    print("\n小提琴图特点:")
    print("- 显示数据的概率密度分布")
    print("- 能看出数据分布的形状（单峰、双峰等）")
    print("- 提供比箱线图更丰富的分布信息")
    print("- 适合分析数据的分布模式")


def generate_report(movies_df):
    """生成电影数据分析报告"""
    print("=" * 60)
    print("                豆瓣电影Top250数据分析报告")
    print("=" * 60)
    
    if movies_df.empty:
        print("错误: 电影数据为空，无法生成报告")
        return
    
    print(f"\n数据概况:")
    print(f"- 爬取电影数量: {len(movies_df)} 部")
    
    if '评分' in movies_df.columns:
        print(f"- 评分范围: {movies_df['评分'].min():.1f} - {movies_df['评分'].max():.1f} 分")
        print(f"- 平均评分: {movies_df['评分'].mean():.2f} 分")
        print(f"- 评分中位数: {movies_df['评分'].median():.2f} 分")
        print(f"- 评分标准差: {movies_df['评分'].std():.2f} 分")
    
    if '排名' in movies_df.columns:
        print(f"- 排名范围: {movies_df['排名'].min()} - {movies_df['排名'].max()}")
    
    # 评分等级统计
    if '评分等级' in movies_df.columns:
        print(f"\n评分等级分布:")
        rating_stats = movies_df['评分等级'].value_counts()
        for level, count in rating_stats.items():
            percentage = (count / len(movies_df)) * 100
            print(f"- {level}: {count}部 ({percentage:.1f}%)")
    
    print(f"\n生成的文件:")
    print("数据文件:")
    print("  - results/movies_data.xlsx - Excel格式原始数据")
    print("  - results/processed_movies_data.xlsx - Excel格式处理后数据（含多个工作表）")
    
    print("\n静态图片 (PNG格式, 高分辨率):")
    print("  - results/movies_rating_boxplot.png - 电影评分分布箱线图")
    print("  - results/movies_rating_violin.png - 电影评分分布小提琴图")
    print("  - results/movies_rating_levels.png - 评分等级分布图")
    print("  - results/movies_rank_distribution.png - 电影排名分布图")
    print("  - results/movies_boxplot.png - 对比分析箱线图")
    print("  - results/movies_violin.png - 对比分析小提琴图")
    
    print("\n使用建议:")
    print("- PNG图片适合用于报告和文档")
    print("- 建议结合多种可视化方法来获得全面的数据洞察")


def export_processed_data_to_excel(movies_df, filename='results/processed_movies_data.xlsx'):
    """导出处理后的数据到Excel文件，包含格式设置"""
    if movies_df.empty:
        print("没有数据可导出")
        return
    
    try:
        # 创建Excel写入器
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # 写入主数据表
            movies_df.to_excel(writer, sheet_name='电影数据', index=False)
            
            # 获取工作表
            worksheet = writer.sheets['电影数据']
            
            # 设置列宽
            column_widths = {
                'A': 25,  # 名称
                'B': 15,  # 图片
                'C': 8,   # 排名
                'D': 8,   # 评分
                'E': 40,  # 作者信息
                'F': 35,  # 简介
                'G': 15   # 评分等级
            }
            
            for col, width in column_widths.items():
                worksheet.column_dimensions[col].width = width
            
            # 如果有评分等级，创建统计表
            if '评分等级' in movies_df.columns:
                rating_stats = movies_df['评分等级'].value_counts().reset_index()
                rating_stats.columns = ['评分等级', '电影数量']
                rating_stats['百分比'] = (rating_stats['电影数量'] / len(movies_df) * 100).round(2)
                
                # 写入统计表
                rating_stats.to_excel(writer, sheet_name='评分等级统计', index=False)
                
                # 设置统计表格式
                stat_worksheet = writer.sheets['评分等级统计']
                stat_worksheet.column_dimensions['A'].width = 15
                stat_worksheet.column_dimensions['B'].width = 12
                stat_worksheet.column_dimensions['C'].width = 12
            
            # 创建数据描述统计表
            if '评分' in movies_df.columns:
                desc_stats = movies_df[['排名', '评分']].describe().round(2)
                desc_stats.to_excel(writer, sheet_name='数据统计')
        
        print(f"处理后的电影数据已导出到Excel文件: {filename}")
        print("Excel文件包含以下工作表:")
        print("  - 电影数据: 完整的电影信息")
        if '评分等级' in movies_df.columns:
            print("  - 评分等级统计: 各评分等级的分布情况")
        print("  - 数据统计: 排名和评分的描述性统计")
        
    except Exception as e:
        print(f"导出Excel文件时出错: {e}")
        print("提示：请确保已安装openpyxl库：pip install openpyxl")


def main():
    """主函数"""
    print("=" * 60)
    print("                豆瓣电影数据爬虫与可视化分析")
    print("=" * 60)
    
    # 1. 数据爬取
    print("\n开始爬取豆瓣电影数据...")
    movie_scraper = DoubanMovieScraper()
    
    # 爬取电影数据
    movies_data = movie_scraper.scrape_movies(max_pages=10)
    
    # 保存数据到Excel
    movie_scraper.save_to_excel()
    
    # 转换为DataFrame
    movies_df = pd.DataFrame(movies_data)
    print(f"\n电影数据形状: {movies_df.shape}")
    
    # 2. 数据处理
    print("\n开始数据处理...")
    movies_df = process_movie_data(movies_df)
    
    # 3. 数据可视化
    print("\n开始数据可视化...")
    
    # 电影数据可视化
    print("\n--- 电影数据可视化 ---")
    visualize_movies_data(movies_df)
    
    # 对比分析
    print("\n--- 箱线图与小提琴图对比分析 ---")
    # compare_visualizations(movies_df)
    
    # 4. 生成报告
    print("\n生成分析报告...")
    generate_report(movies_df)
    
    # 导出处理后的数据到Excel
    export_processed_data_to_excel(movies_df)
    
    print("\n分析完成！")
    print("所有文件已保存到 results/ 文件夹中")


if __name__ == "__main__":
    main()