export type TransactionType = 
  | 'payin'
  | 'payout'
  | 'card_spend'
  | 'card_transfer'
  | 'fee'
  | 'refund'

export type AlertLevel = 
  | 'regular'
  | 'needs_confirmation'
  | 'insufficient_data'

export interface Transaction {
  id: number
  source: string
  source_id: string
  type: TransactionType
  amount: number
  currency: string
  description: string
  merchant_name: string | null
  category: string | null
  transaction_date: string
  created_at: string
  email_match_status: string | null
  is_flagged: boolean
  alert_level: AlertLevel | null
  alert_reason: string | null
  is_subscription: boolean
  subscription_name: string | null
  next_charge_date: string | null
  dispute_deadline: string | null
  masked_card: string | null
}

export interface TransactionListResponse {
  total: number
  transactions: Transaction[]
}

export interface Summary {
  year: number
  month: number
  total_spent: number
  total_income: number
  total_fees: number
  net_flow: number
  by_category: Record<string, number>
  flagged_count: number
  flagged_transactions: Transaction[]
}
