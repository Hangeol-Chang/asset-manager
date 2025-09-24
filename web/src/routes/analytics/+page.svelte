<script>
	import { onMount } from 'svelte';

	let timeRange = '1M';
	let selectedMetric = 'return';
	let portfolioHistory = [];
	let performanceMetrics = {};
	let assetComparison = [];
	let riskMetrics = {};

	const timeRanges = ['1W', '1M', '3M', '6M', '1Y', 'ALL'];
	const metrics = [
		{ value: 'return', label: '수익률' },
		{ value: 'volatility', label: '변동성' },
		{ value: 'sharpe', label: '샤프 비율' },
		{ value: 'drawdown', label: '최대 낙폭' }
	];

	onMount(() => {
		loadAnalyticsData();
	});

	function loadAnalyticsData() {
		// 실제 API 호출로 대체
		portfolioHistory = [
			{ date: '2025-08-24', value: 120000 },
			{ date: '2025-08-31', value: 121500 },
			{ date: '2025-09-07', value: 119800 },
			{ date: '2025-09-14', value: 123400 },
			{ date: '2025-09-21', value: 125678 },
		];

		performanceMetrics = {
			totalReturn: 4.73,
			monthlyReturn: 2.15,
			yearlyReturn: 18.65,
			volatility: 12.34,
			sharpeRatio: 1.51,
			maxDrawdown: -8.45,
			winRate: 67.3
		};

		assetComparison = [
			{ name: 'AAPL', allocation: 15.2, return: 12.5, risk: 8.2, sharpe: 1.53 },
			{ name: 'TSLA', allocation: 8.7, return: 25.3, risk: 18.9, sharpe: 1.34 },
			{ name: 'NVDA', allocation: 12.1, return: 45.2, risk: 28.7, sharpe: 1.58 },
			{ name: 'BTC', allocation: 10.0, return: 67.8, risk: 45.2, sharpe: 1.50 },
			{ name: 'ETH', allocation: 7.5, return: 45.6, risk: 38.1, sharpe: 1.20 }
		];

		riskMetrics = {
			var95: -2.34,
			var99: -4.67,
			expectedShortfall: -5.23,
			beta: 1.15,
			correlation: 0.78
		};
	}

	function handleTimeRangeChange(range) {
		timeRange = range;
		loadAnalyticsData();
	}

	function handleMetricChange(metric) {
		selectedMetric = metric;
	}
</script>

<div class="analytics">
	<header class="analytics-header">
		<h1>Portfolio Analytics</h1>
		<p class="subtitle">심화 분석 및 성과 평가</p>
	</header>

	<div class="controls">
		<div class="time-range-selector">
			<span class="control-label">기간 선택:</span>
			<div class="range-buttons">
				{#each timeRanges as range}
					<button 
						class="range-btn {timeRange === range ? 'active' : ''}"
						on:click={() => handleTimeRangeChange(range)}
					>
						{range}
					</button>
				{/each}
			</div>
		</div>

		<div class="metric-selector">
			<label for="metric">분석 지표:</label>
			<select id="metric" bind:value={selectedMetric} on:change={() => handleMetricChange(selectedMetric)}>
				{#each metrics as metric}
					<option value={metric.value}>{metric.label}</option>
				{/each}
			</select>
		</div>
	</div>

	<div class="analytics-grid">
		<section class="performance-chart">
			<h3>포트폴리오 성과 추이</h3>
			<div class="chart-container">
				<div class="chart-placeholder">
					<div class="chart-line">
						{#each portfolioHistory as point, i}
							<div 
								class="chart-point" 
								style="left: {(i / (portfolioHistory.length - 1)) * 100}%; bottom: {((point.value - 115000) / 15000) * 100}%"
							>
								<div class="tooltip">
									<div>${point.value.toLocaleString()}</div>
									<div>{point.date}</div>
								</div>
							</div>
						{/each}
					</div>
				</div>
				<div class="chart-axes">
					<div class="y-axis">
						<span>$130K</span>
						<span>$125K</span>
						<span>$120K</span>
						<span>$115K</span>
					</div>
					<div class="x-axis">
						{#each portfolioHistory as point}
							<span>{point.date.split('-')[1]}/{point.date.split('-')[2]}</span>
						{/each}
					</div>
				</div>
			</div>
		</section>

		<section class="performance-metrics">
			<h3>성과 지표</h3>
			<div class="metrics-grid">
				<div class="metric-card">
					<span class="metric-label">총 수익률</span>
					<span class="metric-value positive">{performanceMetrics.totalReturn}%</span>
				</div>
				<div class="metric-card">
					<span class="metric-label">월간 수익률</span>
					<span class="metric-value positive">{performanceMetrics.monthlyReturn}%</span>
				</div>
				<div class="metric-card">
					<span class="metric-label">연간 수익률</span>
					<span class="metric-value positive">{performanceMetrics.yearlyReturn}%</span>
				</div>
				<div class="metric-card">
					<span class="metric-label">변동성</span>
					<span class="metric-value">{performanceMetrics.volatility}%</span>
				</div>
				<div class="metric-card">
					<span class="metric-label">샤프 비율</span>
					<span class="metric-value">{performanceMetrics.sharpeRatio}</span>
				</div>
				<div class="metric-card">
					<span class="metric-label">최대 낙폭</span>
					<span class="metric-value negative">{performanceMetrics.maxDrawdown}%</span>
				</div>
				<div class="metric-card">
					<span class="metric-label">승률</span>
					<span class="metric-value">{performanceMetrics.winRate}%</span>
				</div>
			</div>
		</section>

		<section class="asset-comparison">
			<h3>자산별 성과 비교</h3>
			<div class="comparison-table">
				<div class="table-header">
					<span>자산</span>
					<span>비중</span>
					<span>수익률</span>
					<span>위험도</span>
					<span>샤프 비율</span>
				</div>
				{#each assetComparison as asset}
					<div class="table-row">
						<span class="asset-name">{asset.name}</span>
						<span class="allocation">{asset.allocation}%</span>
						<span class="return {asset.return >= 0 ? 'positive' : 'negative'}">{asset.return}%</span>
						<span class="risk">{asset.risk}%</span>
						<span class="sharpe">{asset.sharpe}</span>
					</div>
				{/each}
			</div>
		</section>

		<section class="risk-analysis">
			<h3>위험 분석</h3>
			<div class="risk-metrics">
				<div class="risk-item">
					<span class="risk-label">VaR (95%)</span>
					<span class="risk-value">{riskMetrics.var95}%</span>
					<div class="risk-bar">
						<div class="risk-fill" style="width: {Math.abs(riskMetrics.var95) * 10}%"></div>
					</div>
				</div>
				<div class="risk-item">
					<span class="risk-label">VaR (99%)</span>
					<span class="risk-value">{riskMetrics.var99}%</span>
					<div class="risk-bar">
						<div class="risk-fill" style="width: {Math.abs(riskMetrics.var99) * 10}%"></div>
					</div>
				</div>
				<div class="risk-item">
					<span class="risk-label">Expected Shortfall</span>
					<span class="risk-value">{riskMetrics.expectedShortfall}%</span>
					<div class="risk-bar">
						<div class="risk-fill" style="width: {Math.abs(riskMetrics.expectedShortfall) * 10}%"></div>
					</div>
				</div>
				<div class="risk-item">
					<span class="risk-label">베타</span>
					<span class="risk-value">{riskMetrics.beta}</span>
				</div>
				<div class="risk-item">
					<span class="risk-label">시장 상관계수</span>
					<span class="risk-value">{riskMetrics.correlation}</span>
				</div>
			</div>
		</section>

		<section class="sector-analysis">
			<h3>섹터별 분석</h3>
			<div class="sector-breakdown">
				<div class="sector-item">
					<span class="sector-name">Technology</span>
					<div class="sector-bar">
						<div class="sector-fill tech" style="width: 45%"></div>
					</div>
					<span class="sector-percent">45%</span>
				</div>
				<div class="sector-item">
					<span class="sector-name">Cryptocurrency</span>
					<div class="sector-bar">
						<div class="sector-fill crypto" style="width: 25%"></div>
					</div>
					<span class="sector-percent">25%</span>
				</div>
				<div class="sector-item">
					<span class="sector-name">Healthcare</span>
					<div class="sector-bar">
						<div class="sector-fill healthcare" style="width: 15%"></div>
					</div>
					<span class="sector-percent">15%</span>
				</div>
				<div class="sector-item">
					<span class="sector-name">Finance</span>
					<div class="sector-bar">
						<div class="sector-fill finance" style="width: 10%"></div>
					</div>
					<span class="sector-percent">10%</span>
				</div>
				<div class="sector-item">
					<span class="sector-name">Others</span>
					<div class="sector-bar">
						<div class="sector-fill others" style="width: 5%"></div>
					</div>
					<span class="sector-percent">5%</span>
				</div>
			</div>
		</section>

		<section class="insights">
			<h3>인사이트 및 추천</h3>
			<div class="insight-cards">
				<div class="insight-card warning">
					<div class="insight-icon">⚠️</div>
					<div class="insight-content">
						<h4>높은 집중도 위험</h4>
						<p>Technology 섹터에 45% 집중되어 있습니다. 포트폴리오 다양화를 고려해보세요.</p>
					</div>
				</div>
				<div class="insight-card success">
					<div class="insight-icon">✅</div>
					<div class="insight-content">
						<h4>양호한 샤프 비율</h4>
						<p>1.51의 샤프 비율은 위험 대비 수익이 우수함을 나타냅니다.</p>
					</div>
				</div>
				<div class="insight-card info">
					<div class="insight-icon">💡</div>
					<div class="insight-content">
						<h4>리밸런싱 시점</h4>
						<p>일부 자산의 비중이 목표치를 벗어났습니다. 리밸런싱을 고려해보세요.</p>
					</div>
				</div>
			</div>
		</section>
	</div>
</div>

<style>
	.analytics {
		max-width: 1400px;
		margin: 0 auto;
		padding: 20px;
		font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
	}

	.analytics-header {
		text-align: center;
		margin-bottom: 30px;
	}

	.analytics-header h1 {
		color: #1f2937;
		margin-bottom: 8px;
		font-size: 2.5rem;
	}

	.subtitle {
		color: #6b7280;
		font-size: 1.1rem;
	}

	.controls {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 30px;
		flex-wrap: wrap;
		gap: 20px;
	}

	.time-range-selector .control-label,
	.metric-selector label {
		margin-right: 12px;
		font-weight: 600;
		color: #374151;
	}

	.range-buttons {
		display: inline-flex;
		gap: 8px;
	}

	.range-btn {
		padding: 8px 16px;
		border: 1px solid #d1d5db;
		background: white;
		color: #374151;
		border-radius: 6px;
		cursor: pointer;
		transition: all 0.2s;
		font-weight: 500;
	}

	.range-btn:hover {
		background: #f9fafb;
		border-color: #9ca3af;
	}

	.range-btn.active {
		background: #3b82f6;
		color: white;
		border-color: #3b82f6;
	}

	.metric-selector select {
		padding: 8px 12px;
		border: 1px solid #d1d5db;
		border-radius: 6px;
		background: white;
		color: #374151;
		font-weight: 500;
	}

	.analytics-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
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

	.performance-chart {
		grid-column: span 2;
	}

	.chart-container {
		position: relative;
		height: 300px;
		background: #f9fafb;
		border-radius: 8px;
		padding: 20px;
	}

	.chart-placeholder {
		position: relative;
		height: 100%;
		border-left: 2px solid #d1d5db;
		border-bottom: 2px solid #d1d5db;
	}

	.chart-line {
		position: relative;
		height: 100%;
	}

	.chart-point {
		position: absolute;
		width: 8px;
		height: 8px;
		background: #3b82f6;
		border-radius: 50%;
		cursor: pointer;
		transform: translate(-50%, 50%);
	}

	.chart-point:hover .tooltip {
		display: block;
	}

	.tooltip {
		display: none;
		position: absolute;
		bottom: 20px;
		left: 50%;
		transform: translateX(-50%);
		background: #1f2937;
		color: white;
		padding: 8px 12px;
		border-radius: 6px;
		font-size: 0.85rem;
		white-space: nowrap;
		z-index: 10;
	}

	.chart-axes {
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		pointer-events: none;
	}

	.y-axis {
		position: absolute;
		left: -40px;
		top: 0;
		bottom: 0;
		display: flex;
		flex-direction: column;
		justify-content: space-between;
		font-size: 0.8rem;
		color: #6b7280;
	}

	.x-axis {
		position: absolute;
		bottom: -25px;
		left: 0;
		right: 0;
		display: flex;
		justify-content: space-between;
		font-size: 0.8rem;
		color: #6b7280;
	}

	.metrics-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
		gap: 15px;
	}

	.metric-card {
		background: #f9fafb;
		padding: 15px;
		border-radius: 8px;
		text-align: center;
		border: 1px solid #e5e7eb;
	}

	.metric-label {
		display: block;
		font-size: 0.85rem;
		color: #6b7280;
		margin-bottom: 8px;
	}

	.metric-value {
		display: block;
		font-size: 1.5rem;
		font-weight: 700;
		color: #1f2937;
	}

	.metric-value.positive {
		color: #10b981;
	}

	.metric-value.negative {
		color: #ef4444;
	}

	.comparison-table {
		display: flex;
		flex-direction: column;
		gap: 2px;
	}

	.table-header,
	.table-row {
		display: grid;
		grid-template-columns: 1fr 1fr 1fr 1fr 1fr;
		gap: 15px;
		padding: 12px;
		align-items: center;
	}

	.table-header {
		background: #f3f4f6;
		font-weight: 600;
		color: #374151;
		border-radius: 6px;
	}

	.table-row {
		background: #fafafa;
		border-radius: 4px;
	}

	.asset-name {
		font-weight: 600;
		color: #1f2937;
	}

	.return.positive {
		color: #10b981;
	}

	.return.negative {
		color: #ef4444;
	}

	.risk-metrics {
		display: flex;
		flex-direction: column;
		gap: 15px;
	}

	.risk-item {
		display: flex;
		align-items: center;
		gap: 15px;
	}

	.risk-label {
		flex: 1;
		font-weight: 500;
		color: #374151;
	}

	.risk-value {
		width: 60px;
		text-align: right;
		font-weight: 600;
	}

	.risk-bar {
		flex: 2;
		height: 8px;
		background: #f3f4f6;
		border-radius: 4px;
		overflow: hidden;
	}

	.risk-fill {
		height: 100%;
		background: #ef4444;
		transition: width 0.3s ease;
	}

	.sector-breakdown {
		display: flex;
		flex-direction: column;
		gap: 15px;
	}

	.sector-item {
		display: flex;
		align-items: center;
		gap: 15px;
	}

	.sector-name {
		flex: 1;
		font-weight: 500;
		color: #374151;
	}

	.sector-bar {
		flex: 2;
		height: 12px;
		background: #f3f4f6;
		border-radius: 6px;
		overflow: hidden;
	}

	.sector-fill {
		height: 100%;
		transition: width 0.3s ease;
	}

	.sector-fill.tech { background: #3b82f6; }
	.sector-fill.crypto { background: #f59e0b; }
	.sector-fill.healthcare { background: #10b981; }
	.sector-fill.finance { background: #8b5cf6; }
	.sector-fill.others { background: #6b7280; }

	.sector-percent {
		width: 40px;
		text-align: right;
		font-weight: 600;
		color: #374151;
	}

	.insight-cards {
		display: flex;
		flex-direction: column;
		gap: 15px;
	}

	.insight-card {
		display: flex;
		align-items: flex-start;
		gap: 15px;
		padding: 15px;
		border-radius: 8px;
		border-left: 4px solid;
	}

	.insight-card.warning {
		background: #fef3cd;
		border-left-color: #f59e0b;
	}

	.insight-card.success {
		background: #d1fae5;
		border-left-color: #10b981;
	}

	.insight-card.info {
		background: #dbeafe;
		border-left-color: #3b82f6;
	}

	.insight-icon {
		font-size: 1.2rem;
		margin-top: 2px;
	}

	.insight-content h4 {
		margin: 0 0 8px 0;
		font-size: 1rem;
		font-weight: 600;
		color: #1f2937;
	}

	.insight-content p {
		margin: 0;
		font-size: 0.9rem;
		color: #4b5563;
		line-height: 1.5;
	}

	@media (max-width: 768px) {
		.analytics-grid {
			grid-template-columns: 1fr;
		}
		
		.performance-chart {
			grid-column: span 1;
		}
		
		.controls {
			flex-direction: column;
			align-items: stretch;
		}
		
		.metrics-grid {
			grid-template-columns: repeat(2, 1fr);
		}
		
		.table-header,
		.table-row {
			font-size: 0.8rem;
			gap: 8px;
		}
	}
</style>
