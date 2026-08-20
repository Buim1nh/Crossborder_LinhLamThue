'use client'

import { Transaction } from '@/types/transaction'

interface TransactionListProps {
  transactions: Transaction[]
}

export default function TransactionList({ transactions }: TransactionListProps) {
  const getTypeColor = (type: string) => {
    switch (type) {
      case 'payin': return 'text-green-600 bg-green-50'
      case 'payout': return 'text-red-600 bg-red-50'
      case 'card_spend': return 'text-orange-600 bg-orange-50'
      case 'fee': return 'text-gray-600 bg-gray-50'
      default: return 'text-blue-600 bg-blue-50'
    }
  }

  const getTypeLabel = (type: string) => {
    switch (type) {
      case 'payin': return 'Pay In'
      case 'payout': return 'Pay Out'
      case 'card_spend': return 'Card'
      case 'card_transfer': return 'Transfer'
      case 'fee': return 'Fee'
      case 'refund': return 'Refund'
      default: return type
    }
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount)
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    })
  }

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">Recent Transactions</h2>
        <p className="text-sm text-gray-500">{transactions.length} transactions</p>
      </div>
      
      <div className="divide-y divide-gray-100">
        {transactions.length === 0 ? (
          <div className="px-6 py-8 text-center text-gray-500">
            <p>No transactions yet. Upload a statement to get started.</p>
          </div>
        ) : (
          transactions.slice(0, 10).map((tx) => (
            <div key={tx.id} className="px-6 py-4 hover:bg-gray-50 transition-colors">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className={`px-2 py-1 rounded text-xs font-medium ${getTypeColor(tx.type)}`}>
                    {getTypeLabel(tx.type)}
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">
                      {tx.merchant_name || tx.description?.slice(0, 30) || 'Unknown'}
                    </p>
                    <p className="text-sm text-gray-500">
                      {formatDate(tx.transaction_date)}
                      {tx.is_flagged && (
                        <span className="ml-2 text-amber-600">⚠️ Flagged</span>
                      )}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className={`font-semibold ${
                    tx.type === 'payin' ? 'text-green-600' : 'text-gray-900'
                  }`}>
                    {tx.type === 'payin' ? '+' : '-'}{formatCurrency(tx.amount)}
                  </p>
                  {tx.masked_card && (
                    <p className="text-xs text-gray-400">**** {tx.masked_card}</p>
                  )}
                </div>
              </div>
              {tx.alert_reason && (
                <div className="mt-2 text-sm text-amber-600 bg-amber-50 rounded px-2 py-1">
                  {tx.alert_reason}
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  )
}
