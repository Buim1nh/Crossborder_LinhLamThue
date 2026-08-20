interface TabsProps {
  activeTab: 'dashboard' | 'chat' | 'alerts'
  onTabChange: (tab: 'dashboard' | 'chat' | 'alerts') => void
}

export default function Tabs({ activeTab, onTabChange }: TabsProps) {
  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: '📊' },
    { id: 'chat', label: 'Chat', icon: '💬' },
    { id: 'alerts', label: 'Alerts', icon: '🔔' },
  ]

  return (
    <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg w-fit mb-6">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          onClick={() => onTabChange(tab.id as any)}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
            activeTab === tab.id
              ? 'bg-white text-blue-600 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <span className="mr-2">{tab.icon}</span>
          {tab.label}
        </button>
      ))}
    </div>
  )
}
