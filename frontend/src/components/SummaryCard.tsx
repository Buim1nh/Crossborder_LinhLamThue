'use client'

interface SummaryCardProps {
  title: string
  summary: any
}

export default function SummaryCard({ title, summary }: SummaryCardProps) {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount || 0)
  }

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">{title}</h2>
      </div>
      
      <div className="p-6">
        {summary ? (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <p className="text-sm text-gray-500 mb-1">Total Spent</p>
              <p className="text-xl font-bold text-gray-900">
                {formatCurrency(summary.total_spent)}
              </p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-500 mb-1">Total Income</p>
              <p className="text-xl font-bold text-green-600">
                {formatCurrency(summary.total_income)}
              </p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-500 mb-1">Fees</p>
              <p className="text-xl font-bold text-gray-600">
                {formatCurrency(summary.total_fees)}
              </p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-500 mb-1">Net Flow</p>
              <p className={`text-xl font-bold ${
                (summary.net_flow || 0) >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                {formatCurrency(summary.net_flow)}
              </p>
            </div>
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <p>Upload statements to see your summary</p>
          </div>
        )}
        
        {/* Category breakdown would go here */}
        {summary?.by_category && Object.keys(summary.by_category).length > 0 && (
          <div className="mt-6 pt-6 border-t border-gray-100">
            <h3 className="text-sm font-medium text-gray-700 mb-3">By Category</h3>
            <div className="space-y-2">
              {Object.entries(summary.by_category)
                .sort(([, a]: [string, number], [, b]: [string, number]) => b - a)
                .slice(0, 5)
                .map(([category, amount]) => (
                  <div key={category} className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">{category}</span>
                    <span className="text-sm font-medium">{formatCurrency(amount as number)}</span>
                  </div>
                ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
