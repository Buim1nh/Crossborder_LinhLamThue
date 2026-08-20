'use client'

import { useState } from 'react'
import Header from '@/components/Header'
import FileUpload from '@/components/FileUpload'
import TransactionList from '@/components/TransactionList'
import SummaryCard from '@/components/SummaryCard'
import ChatInterface from '@/components/ChatInterface'
import Tabs from '@/components/Tabs'

export default function Home() {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'chat' | 'alerts'>('dashboard')
  const [transactions, setTransactions] = useState<any[]>([])
  const [summary, setSummary] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(false)

  const handleFileUpload = async (source: string, file: File) => {
    setIsLoading(true)
    try {
      const formData = new FormData()
      formData.append('source', source)
      formData.append('file', file)

      const response = await fetch('http://localhost:8000/api/transactions/upload/statement', {
        method: 'POST',
        body: formData,
      })

      if (response.ok) {
        const data = await response.json()
        console.log('Uploaded:', data)
        // Refresh transactions list
        const txResponse = await fetch('http://localhost:8000/api/transactions')
        if (txResponse.ok) {
          const txData = await txResponse.json()
          setTransactions(txData.transactions)
        }
      }
    } catch (error) {
      console.error('Upload failed:', error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <main className="min-h-screen">
      <Header />
      
      <div className="container mx-auto px-4 py-6">
        {/* Tab Navigation */}
        <Tabs activeTab={activeTab} onTabChange={setActiveTab} />
        
        {/* Upload Section - Always visible on dashboard */}
        {activeTab === 'dashboard' && (
          <div className="mb-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <FileUpload
                title="Account Statement"
                source="account"
                acceptedFormats=".csv,.pdf"
                onUpload={handleFileUpload}
                isLoading={isLoading}
              />
              <FileUpload
                title="Wallet Balance"
                source="wallet"
                acceptedFormats=".csv,.pdf"
                onUpload={handleFileUpload}
                isLoading={isLoading}
              />
              <FileUpload
                title="Card Statement"
                source="card"
                acceptedFormats=".csv,.pdf"
                onUpload={handleFileUpload}
                isLoading={isLoading}
              />
            </div>
          </div>
        )}

        {/* Dashboard Content */}
        {activeTab === 'dashboard' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="space-y-6">
              <SummaryCard title="Monthly Summary" summary={summary} />
              <TransactionList transactions={transactions} />
            </div>
            <div>
              <ChatInterface />
            </div>
          </div>
        )}

        {/* Chat Interface */}
        {activeTab === 'chat' && (
          <div className="max-w-4xl mx-auto">
            <ChatInterface fullPage />
          </div>
        )}

        {/* Alerts */}
        {activeTab === 'alerts' && (
          <div className="max-w-4xl mx-auto">
            <h2 className="text-xl font-semibold mb-4">Alerts & Notifications</h2>
            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-gray-500">No alerts at the moment.</p>
            </div>
          </div>
        )}
      </div>

      {/* Disclaimer Banner */}
      <div className="fixed bottom-0 left-0 right-0 bg-amber-50 border-t border-amber-200 p-3">
        <p className="text-center text-sm text-amber-800">
          <span className="font-medium">⚠️ Disclaimer:</span> This tool only assists you in reviewing finances. 
          Results are for reference only, not official conclusions from Wealify. 
          If you notice unusual transactions, please contact support immediately — in the US, the dispute deadline is 60 days from the statement date.
        </p>
      </div>
    </main>
  )
}
