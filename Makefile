.PHONY: help install run test mock clean setup-crontab

help:
	@echo "🚀 拓品智能体分析系统 - 命令帮助"
	@echo ""
	@echo "可用命令:"
	@echo "  make install         - 安装依赖"
	@echo "  make run            - 运行完整分析"
	@echo "  make mock           - 使用模拟数据测试"
	@echo "  make debug          - 调试模式运行"
	@echo "  make clean          - 清理缓存和日志"
	@echo "  make setup-crontab  - 配置本地定时任务"
	@echo "  make test           - 运行测试"
	@echo ""

install:
	pip install -r requirements.txt
	cp .env.example .env
	@echo "✅ 依赖安装完成，请编辑 .env 文件配置 API Key"

run:
	python scheduler.py

mock:
	python scheduler.py --mock

debug:
	DEBUG=true LOG_LEVEL=DEBUG python scheduler.py --debug

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -f scheduler.log
	@echo "✅ 清理完成"

setup-crontab:
	@echo "设置本地定时任务 (macOS/Linux)"
	@echo "编辑 crontab，添加以下行:"
	@echo ""
	@echo "0 8 * * * cd $(PWD) && python scheduler.py >> scheduler.log 2>&1"
	@echo ""
	@echo "运行以下命令进行编辑:"
	@echo "crontab -e"

test:
	@echo "运行测试..."
	python scheduler.py --mock
	@echo "✅ 测试完成"

.DEFAULT_GOAL := help
