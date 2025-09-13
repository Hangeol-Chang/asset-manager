"""
Asset Manager Database Module

SQLite 데이터베이스를 사용한 자산 관리 시스템
"""

import sqlite3
import os
import logging
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger('asset-manager')

class AssetManagerDB:
    def __init__(self, db_path: str = None):
        """데이터베이스 초기화"""
        if db_path is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(current_dir, 'data', 'asset_manager.db')
        
        # 데이터 디렉토리 생성
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """데이터베이스 연결 반환"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # 딕셔너리 형태로 결과 반환
        return conn
    
    def init_database(self):
        """데이터베이스 테이블 초기화"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 카테고리 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL CHECK (type IN ('income', 'expense')),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 거래 내역 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL CHECK (type IN ('income', 'expense')),
                    amount REAL NOT NULL,
                    category_id INTEGER,
                    description TEXT,
                    date DATE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES categories (id)
                )
            ''')
            
            # 자산 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS assets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL CHECK (type IN ('cash', 'bank', 'investment', 'real_estate', 'other')),
                    amount REAL NOT NULL DEFAULT 0,
                    currency TEXT DEFAULT 'KRW',
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            
            # 기본 카테고리 데이터 삽입
            self._insert_default_categories(cursor)
            conn.commit()
    
    def _insert_default_categories(self, cursor):
        """기본 카테고리 데이터 삽입"""
        # 기존 카테고리가 있는지 확인
        cursor.execute('SELECT COUNT(*) FROM categories')
        if cursor.fetchone()[0] > 0:
            return
        
        default_categories = [
            ('급여', 'income'),
            ('부업', 'income'),
            ('투자수익', 'income'),
            ('기타수입', 'income'),
            ('식비', 'expense'),
            ('교통비', 'expense'),
            ('주거비', 'expense'),
            ('의료비', 'expense'),
            ('쇼핑', 'expense'),
            ('여가', 'expense'),
            ('교육', 'expense'),
            ('기타지출', 'expense')
        ]
        
        cursor.executemany(
            'INSERT INTO categories (name, type) VALUES (?, ?)',
            default_categories
        )
    
    # 거래 내역 관련 메서드
    def add_transaction(self, transaction_type: str, amount: float, 
                       category_id: int, description: str = None, 
                       date: str = None) -> int:
        """거래 내역 추가"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO transactions (type, amount, category_id, description, date)
                VALUES (?, ?, ?, ?, ?)
            ''', (transaction_type, amount, category_id, description, date))
            conn.commit()
            return cursor.lastrowid
    
    def get_transactions(self, start_date: str = None, end_date: str = None,
                        transaction_type: str = None, category_id: int = None,
                        limit: int = None) -> List[Dict]:
        """거래 내역 조회"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            query = '''
                SELECT t.*, c.name as category_name
                FROM transactions t
                LEFT JOIN categories c ON t.category_id = c.id
                WHERE 1=1
            '''
            params = []
            
            if start_date:
                query += ' AND t.date >= ?'
                params.append(start_date)
            
            if end_date:
                query += ' AND t.date <= ?'
                params.append(end_date)
            
            if transaction_type:
                query += ' AND t.type = ?'
                params.append(transaction_type)
            
            if category_id:
                query += ' AND t.category_id = ?'
                params.append(category_id)
            
            query += ' ORDER BY t.date DESC, t.created_at DESC'
            
            if limit:
                query += ' LIMIT ?'
                params.append(limit)
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def update_transaction(self, transaction_id: int, **kwargs) -> bool:
        """거래 내역 수정"""
        if not kwargs:
            return False
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 업데이트할 필드들 구성
            set_clauses = []
            params = []
            
            for field, value in kwargs.items():
                if field in ['type', 'amount', 'category_id', 'description', 'date']:
                    set_clauses.append(f'{field} = ?')
                    params.append(value)
            
            if not set_clauses:
                return False
            
            set_clauses.append('updated_at = CURRENT_TIMESTAMP')
            params.append(transaction_id)
            
            query = f'''
                UPDATE transactions 
                SET {', '.join(set_clauses)}
                WHERE id = ?
            '''
            
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_transaction(self, transaction_id: int) -> bool:
        """거래 내역 삭제"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM transactions WHERE id = ?', (transaction_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    # 카테고리 관련 메서드
    def get_categories(self, category_type: str = None) -> List[Dict]:
        """카테고리 조회"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if category_type:
                cursor.execute(
                    'SELECT * FROM categories WHERE type = ? ORDER BY name',
                    (category_type,)
                )
            else:
                cursor.execute('SELECT * FROM categories ORDER BY type, name')
            
            return [dict(row) for row in cursor.fetchall()]
    
    def add_category(self, name: str, category_type: str) -> int:
        """카테고리 추가"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO categories (name, type) VALUES (?, ?)',
                (name, category_type)
            )
            conn.commit()
            return cursor.lastrowid
    
    # 통계 관련 메서드
    def get_monthly_summary(self, year: int, month: int) -> Dict:
        """월별 수입/지출 요약"""
        start_date = f'{year:04d}-{month:02d}-01'
        if month == 12:
            end_date = f'{year+1:04d}-01-01'
        else:
            end_date = f'{year:04d}-{month+1:02d}-01'
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 수입 합계
            cursor.execute('''
                SELECT COALESCE(SUM(amount), 0) 
                FROM transactions 
                WHERE type = 'income' AND date >= ? AND date < ?
            ''', (start_date, end_date))
            income = cursor.fetchone()[0]
            
            # 지출 합계
            cursor.execute('''
                SELECT COALESCE(SUM(amount), 0) 
                FROM transactions 
                WHERE type = 'expense' AND date >= ? AND date < ?
            ''', (start_date, end_date))
            expense = cursor.fetchone()[0]
            
            return {
                'income': income,
                'expense': expense,
                'balance': income - expense
            }
    
    def get_category_summary(self, start_date: str = None, end_date: str = None) -> Dict:
        """카테고리별 지출 요약"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            query = '''
                SELECT c.name, c.type, COALESCE(SUM(t.amount), 0) as total
                FROM categories c
                LEFT JOIN transactions t ON c.id = t.category_id
            '''
            params = []
            
            if start_date or end_date:
                query += ' AND ('
                conditions = []
                if start_date:
                    conditions.append('t.date >= ?')
                    params.append(start_date)
                if end_date:
                    conditions.append('t.date <= ?')
                    params.append(end_date)
                query += ' OR '.join(conditions) + ')'
            
            query += ' GROUP BY c.id, c.name, c.type ORDER BY c.type, total DESC'
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            summary = {'income': {}, 'expense': {}}
            for row in results:
                summary[row['type']][row['name']] = row['total']
            
            return summary
