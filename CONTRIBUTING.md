# 贡献指南

感谢你对 PathoMind 项目的关注！我们欢迎各种形式的贡献。

## 如何贡献

### 报告问题

如果你发现了bug或有功能建议：

1. 先在 [Issues](https://github.com/yourusername/pathomind/issues) 中搜索是否已有相关问题
2. 如果没有，创建一个新的Issue，并提供：
   - 清晰的标题和描述
   - 复现步骤（如果是bug）
   - 期望的行为
   - 实际的行为
   - 环境信息（Python版本、操作系统等）

### 提交代码

1. **Fork 仓库**
   ```bash
   # 在GitHub上点击Fork按钮
   git clone https://github.com/your-username/pathomind.git
   cd pathomind
   ```

2. **创建分支**
   ```bash
   git checkout -b feature/your-feature-name
   # 或
   git checkout -b fix/your-bug-fix
   ```

3. **设置开发环境**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -e ".[dev]"
   ```

4. **编写代码**
   - 遵循项目的代码风格（使用Ruff进行格式化）
   - 为新功能添加测试
   - 确保所有测试通过
   - 更新相关文档

5. **运行测试**
   ```bash
   # 运行所有测试
   pytest
   
   # 运行特定类型的测试
   pytest tests/unit/
   pytest tests/integration/
   
   # 检查代码风格
   ruff check src/ tests/
   
   # 类型检查
   mypy src/
   ```

6. **提交更改**
   ```bash
   git add .
   git commit -m "feat: add amazing feature"
   # 或
   git commit -m "fix: resolve issue with X"
   ```

   提交信息格式：
   - `feat:` 新功能
   - `fix:` Bug修复
   - `docs:` 文档更新
   - `test:` 测试相关
   - `refactor:` 代码重构
   - `perf:` 性能优化
   - `chore:` 构建/工具相关

7. **推送到GitHub**
   ```bash
   git push origin feature/your-feature-name
   ```

8. **创建Pull Request**
   - 在GitHub上创建Pull Request
   - 填写PR模板，描述你的更改
   - 等待代码审查

## 代码规范

### Python代码风格

- 遵循 PEP 8 规范
- 使用 Ruff 进行代码格式化和检查
- 使用类型注解（Type Hints）
- 函数和类需要有文档字符串

示例：
```python
def process_document(
    document: str,
    chunk_size: int = 1000,
    overlap: int = 200
) -> list[str]:
    """
    Process a document into chunks.
    
    Args:
        document: The input document text
        chunk_size: Size of each chunk in characters
        overlap: Overlap between chunks
        
    Returns:
        List of document chunks
    """
    # Implementation here
    pass
```

### 测试规范

- 为新功能编写单元测试
- 测试覆盖率应保持在80%以上
- 使用有意义的测试名称
- 使用pytest的fixture进行测试设置

示例：
```python
def test_document_chunking_with_overlap():
    """Test that document chunking respects overlap parameter."""
    document = "A" * 1000
    chunks = process_document(document, chunk_size=500, overlap=100)
    
    assert len(chunks) == 3
    assert len(chunks[0]) == 500
```

### 文档规范

- 更新相关的README和文档
- 为新功能添加使用示例
- 保持文档的中英文版本同步（如适用）

## 开发流程

### 分支策略

- `main`: 稳定的生产版本
- `develop`: 开发分支
- `feature/*`: 新功能分支
- `fix/*`: Bug修复分支

### 版本发布

我们使用语义化版本（Semantic Versioning）：
- MAJOR: 不兼容的API更改
- MINOR: 向后兼容的新功能
- PATCH: 向后兼容的Bug修复

## 社区准则

- 尊重所有贡献者
- 保持友好和专业的交流
- 接受建设性的批评
- 关注项目的最佳利益

## 需要帮助？

如果你在贡献过程中遇到问题：

- 查看 [文档](docs/)
- 在 [Issues](https://github.com/yourusername/pathomind/issues) 中提问
- 联系维护者

再次感谢你的贡献！🎉
