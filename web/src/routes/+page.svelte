<script>
	import { onMount } from 'svelte';

	let portfolioValue = 0;
	let todayChange = 0;
	let changePercent = 0;
	let recentTransactions = [];
	let assetAllocation = [];

	onMount(async () => {
		// 실제 API 호출로 대체
		portfolioValue = 125678.90;
		todayChange = 2453.12;
		changePercent = 1.98;
		
		recentTransactions = [
			{ id: 1, type: 'BUY', asset: 'AAPL', amount: 10, price: 175.25, date: '2025-09-24' },
			{ id: 2, type: 'SELL', asset: 'TSLA', amount: 5, price: 245.80, date: '2025-09-23' },
			{ id: 3, type: 'BUY', asset: 'NVDA', amount: 3, price: 425.60, date: '2025-09-22' },
		];

		assetAllocation = [
			{ category: 'Stocks', value: 75234.50, percent: 59.9 },
			{ category: 'Crypto', value: 30123.40, percent: 24.0 },
			{ category: 'Bonds', value: 15321.00, percent: 12.2 },
			{ category: 'Cash', value: 5000.00, percent: 3.9 },
		];
	});
</script>

<div class="dashboard">
	<header class="dashboard-header">
		<h1>Asset Manager Dashboard</h1>
		<p class="subtitle">포트폴리오 관리 및 자산 추적</p>
	</header>

	<div class="portfolio-overview">
		<div class="portfolio-card">
			<h2>총 포트폴리오 가치</h2>
			<div class="portfolio-value">
				<span class="value">${portfolioValue.toLocaleString()}</span>
				<span class="change {todayChange >= 0 ? 'positive' : 'negative'}">
					{todayChange >= 0 ? '+' : ''}{todayChange.toLocaleString()} ({changePercent}%)
				</span>
			</div>
		</div>
	</div>

	<div class="dashboard-grid">
		<section class="recent-transactions">
			<h3>최근 거래</h3>
			<div class="transaction-list">
				{#each recentTransactions as transaction}
					<div class="transaction-item">
						<div class="transaction-info">
							<span class="transaction-type {transaction.type.toLowerCase()}">{transaction.type}</span>
							<span class="asset-name">{transaction.asset}</span>
						</div>
						<div class="transaction-details">
							<span class="amount">{transaction.amount}주</span>
							<span class="price">${transaction.price}</span>
							<span class="date">{transaction.date}</span>
						</div>
					</div>
				{/each}
			</div>
			<a href="/transactions" class="view-all">모든 거래 보기 →</a>
		</section>

		<section class="asset-allocation">
			<h3>자산 배분</h3>
			<div class="allocation-chart">
				{#each assetAllocation as asset}
					<div class="allocation-item">
						<div class="allocation-bar">
							<div class="bar-fill" style="width: {asset.percent}%"></div>
						</div>
						<div class="allocation-info">
							<span class="category">{asset.category}</span>
							<span class="value">${asset.value.toLocaleString()}</span>
							<span class="percent">{asset.percent}%</span>
						</div>
					</div>
				{/each}
			</div>
			<a href="/analytics" class="view-all">상세 분석 보기 →</a>
		</section>

		<section class="quick-actions">
			<h3>빠른 작업</h3>
			<div class="action-buttons">
				<button class="action-btn buy">새 거래 추가</button>
				<button class="action-btn">포트폴리오 리밸런싱</button>
				<button class="action-btn">수익률 보고서</button>
				<button class="action-btn">알림 설정</button>
			</div>
		</section>

		<section class="market-summary">
			<h3>시장 현황</h3>
			<div class="market-indices">
				<div class="index-item">
					<span class="index-name">S&P 500</span>
					<span class="index-value">4,567.23</span>
					<span class="index-change positive">+1.25%</span>
				</div>
				<div class="index-item">
					<span class="index-name">NASDAQ</span>
					<span class="index-value">14,329.76</span>
					<span class="index-change positive">+2.08%</span>
				</div>
				<div class="index-item">
					<span class="index-name">Bitcoin</span>
					<span class="index-value">$63,425</span>
					<span class="index-change negative">-0.45%</span>
				</div>
			</div>
		</section>
	</div>
</div>

<style>
	.dashboard {
		max-width: 1200px;
		margin: 0 auto;
		padding: 20px;
		font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
	}

	.dashboard-header {
		text-align: center;
		margin-bottom: 30px;
	}

	.dashboard-header h1 {
		color: #1f2937;
		margin-bottom: 8px;
		font-size: 2.5rem;
	}

	.subtitle {
		color: #6b7280;
		font-size: 1.1rem;
	}

	.portfolio-overview {
		margin-bottom: 30px;
	}

	.portfolio-card {
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
		padding: 30px;
		border-radius: 15px;
		text-align: center;
		box-shadow: 0 8px 25px rgba(0,0,0,0.15);
	}

	.portfolio-card h2 {
		margin-bottom: 15px;
		font-weight: 300;
		opacity: 0.9;
	}

	.portfolio-value .value {
		display: block;
		font-size: 3rem;
		font-weight: 700;
		margin-bottom: 10px;
	}

	.change {
		font-size: 1.2rem;
		font-weight: 600;
	}

	.change.positive {
		color: #10b981;
	}

	.change.negative {
		color: #ef4444;
	}

	.dashboard-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
		gap: 25px;
	}

	section {
		background: white;
		padding: 25px;
		border-radius: 12px;
		box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
		border: 1px solid #e5e7eb;
	}

	section h3 {
		margin-bottom: 20px;
		color: #1f2937;
		font-size: 1.3rem;
		border-bottom: 2px solid #e5e7eb;
		padding-bottom: 10px;
	}

	.transaction-item {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 15px 0;
		border-bottom: 1px solid #f3f4f6;
	}

	.transaction-item:last-child {
		border-bottom: none;
	}

	.transaction-type {
		padding: 4px 8px;
		border-radius: 6px;
		font-size: 0.85rem;
		font-weight: 600;
		margin-right: 10px;
	}

	.transaction-type.buy {
		background: #dcfce7;
		color: #16a34a;
	}

	.transaction-type.sell {
		background: #fee2e2;
		color: #dc2626;
	}

	.asset-name {
		font-weight: 600;
		color: #1f2937;
	}

	.transaction-details {
		text-align: right;
		color: #6b7280;
		font-size: 0.9rem;
	}

	.allocation-item {
		margin-bottom: 15px;
	}

	.allocation-bar {
		height: 8px;
		background: #f3f4f6;
		border-radius: 4px;
		margin-bottom: 8px;
		overflow: hidden;
	}

	.bar-fill {
		height: 100%;
		background: linear-gradient(90deg, #3b82f6, #06b6d4);
		transition: width 0.3s ease;
	}

	.allocation-info {
		display: flex;
		justify-content: space-between;
		align-items: center;
		font-size: 0.9rem;
	}

	.category {
		font-weight: 600;
		color: #1f2937;
	}

	.value, .percent {
		color: #6b7280;
	}

	.action-buttons {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 12px;
	}

	.action-btn {
		padding: 12px 16px;
		border: 1px solid #d1d5db;
		background: white;
		color: #374151;
		border-radius: 8px;
		cursor: pointer;
		transition: all 0.2s;
		font-weight: 500;
	}

	.action-btn:hover {
		background: #f9fafb;
		border-color: #9ca3af;
	}

	.action-btn.buy {
		background: #059669;
		color: white;
		border-color: #059669;
	}

	.action-btn.buy:hover {
		background: #047857;
	}

	.index-item {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 12px 0;
		border-bottom: 1px solid #f3f4f6;
	}

	.index-item:last-child {
		border-bottom: none;
	}

	.index-name {
		font-weight: 600;
		color: #1f2937;
	}

	.index-value {
		font-weight: 600;
	}

	.index-change {
		font-weight: 600;
		font-size: 0.9rem;
	}

	.view-all {
		display: inline-block;
		margin-top: 15px;
		color: #3b82f6;
		text-decoration: none;
		font-weight: 500;
		transition: color 0.2s;
	}

	.view-all:hover {
		color: #1d4ed8;
	}

	@media (max-width: 768px) {
		.dashboard-grid {
			grid-template-columns: 1fr;
		}
		
		.portfolio-value .value {
			font-size: 2.5rem;
		}
		
		.action-buttons {
			grid-template-columns: 1fr;
		}
	}
</style>
