echo "# v1.0.30 数据库基线说明

## 版本信息
- 数据库基线版本：v1.0.30
- 生成时间：2025-12-31
- 对应 Git 版本：v1.0.30
- 数据库：ai_generation_platform

## 备份内容
1. **aiweb_schema_v1.0.30.sql**  
   完整的 schema 定义（无业务数据）
2. **aiweb_constraints_v1.0.30.txt**  
   表约束信息
3. **aiweb_sequences_v1.0.30.txt**  
   序列信息
4. **aiweb_indexes_v1.0.30.txt**  
   索引信息
5. **aiweb_tables_columns_v1.0.30.txt**  
   表字段信息
6. **aiweb_tables_overview_v1.0.30.txt**  
   表结构概览
7. **aiweb_schema_v1.0.30.sha256**  
   用于校验 schema 文件完整性

## 法律声明
此备份文件作为 v1.0.30 版本数据库的基线文件，用于后续版本对比、迁移与回滚。此文件与项目宪法、版本事实回写窗口一同存档，具有法律效力。

## 使用说明
- `aiweb_schema_v1.0.30.sql` 用于初始化数据库结构
- 其他文件用于查询、验证与对比" > db/backups/v1.0.30/README.md
