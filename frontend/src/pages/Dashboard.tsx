import React from 'react'
import { BarChart3, TrendingUp, Users, DollarSign } from 'lucide-react'

const Dashboard: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* KPI Cards */}
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-500 text-sm">Total Revenue</p>
              <p className="text-3xl font-bold text-gray-800">Rp 25.5M</p>
            </div>
            <BarChart3 size={40} className="text-blue-500" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-500 text-sm">Total Commission</p>
              <p className="text-3xl font-bold text-gray-800">Rp 2.5M</p>
            </div>
            <DollarSign size={40} className="text-green-500" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-500 text-sm">Active Employees</p>
              <p className="text-3xl font-bold text-gray-800">9</p>
            </div>
            <Users size={40} className="text-purple-500" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-500 text-sm">Active Campaigns</p>
              <p className="text-3xl font-bold text-gray-800">5</p>
            </div>
            <TrendingUp size={40} className="text-orange-500" />
          </div>
        </div>
      </div>

      {/* Charts Placeholder */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4 text-gray-800">Revenue Trend</h3>
          <div className="h-64 bg-gray-100 rounded flex items-center justify-center">
            <p className="text-gray-500">Chart coming soon...</p>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4 text-gray-800">Top Performers</h3>
          <div className="space-y-3">
            {[
              { name: 'John Host', commission: 'Rp 500K' },
              { name: 'Jane Leader', commission: 'Rp 450K' },
              { name: 'Mike Host', commission: 'Rp 400K' },
            ].map((person, i) => (
              <div key={i} className="flex justify-between p-3 bg-gray-50 rounded">
                <span className="font-medium">{person.name}</span>
                <span className="text-green-600 font-semibold">{person.commission}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
