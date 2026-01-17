import React, { useState, useEffect } from 'react'
import Modal from '@/components/Modal'
import AccountForm from '@/components/forms/AccountForm'
import { accountApi } from '@/api/accounts'
import { ShopeeAccount } from '@/types'

const Accounts: React.FC = () => {
  const [accounts, setAccounts] = useState<ShopeeAccount[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedAccount, setSelectedAccount] = useState<ShopeeAccount | undefined>()
  const studioId = 1 // Default studio

  const fetchAccounts = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await accountApi.getAll(studioId)
      setAccounts(data)
    } catch (error: any) {
      console.error('Failed to fetch accounts:', error)
      setError(error.message || 'Failed to load accounts')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAccounts()
  }, [])

  const handleAddAccount = () => {
    setSelectedAccount(undefined)
    setIsModalOpen(true)
  }

  const handleEditAccount = (account: ShopeeAccount) => {
    setSelectedAccount(account)
    setIsModalOpen(true)
  }

  const handleSubmit = async (data: Partial<ShopeeAccount>) => {
    try {
      if (selectedAccount) {
        await accountApi.update(selectedAccount.id, data)
      } else {
        await accountApi.create(data as Omit<ShopeeAccount, 'id' | 'created_at'>)
      }
      setIsModalOpen(false)
      fetchAccounts()
    } catch (error) {
      console.error('Failed to save account:', error)
      alert('Failed to save account. Please try again.')
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this account?')) return

    try {
      await accountApi.delete(id)
      fetchAccounts()
    } catch (error) {
      console.error('Failed to delete account:', error)
      alert('Failed to delete account. Please try again.')
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative" role="alert">
        <strong className="font-bold">Error! </strong>
        <span className="block sm:inline">{error}</span>
        <button
          onClick={fetchAccounts}
          className="mt-2 bg-red-100 px-3 py-1 rounded text-sm font-semibold hover:bg-red-200"
        >
          Retry
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <h1 className="text-3xl font-bold text-gray-800">Akun Shopee</h1>
            <div className="group relative">
              <div className="bg-slate-200 hover:bg-slate-300 text-slate-600 rounded-full w-5 h-5 flex items-center justify-center text-xs cursor-help">?</div>
              <div className="absolute left-full top-1/2 -translate-y-1/2 ml-2 px-3 py-1 bg-slate-800 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10 pointer-events-none">
                Tempat ngatur semua akun toko.
              </div>
            </div>
          </div>
          <p className="text-gray-500">Kelola semua akun Shopee kamu di sini, jangan sampai ada yang mati.</p>
        </div>
        <div className="flex gap-3">
          <a
            href="/shopee-scraper-extension.zip"
            download
            className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 flex items-center gap-2"
          >
            <span>📥</span>
            Download Extension
          </a>
          <button
            onClick={handleAddAccount}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
          >
            Add Account
          </button>
        </div>
      </div>

      {accounts.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
          No accounts found. Click "Add Account" to create one.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {accounts.map((account) => (
            <div key={account.id} className="bg-white rounded-lg shadow p-6">
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-lg font-semibold text-gray-800">{account.account_name}</h3>
                <span
                  className={`px-2 py-1 rounded text-xs font-semibold ${account.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-500'
                    }`}
                >
                  {account.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>

              <div className="space-y-3 text-sm text-gray-600">
                <div className="flex justify-between">
                  <span>Account ID:</span>
                  <span className="font-semibold text-gray-800">{account.shopee_account_id}</span>
                </div>
                <div className="flex justify-between">
                  <span>Created:</span>
                  <span className="font-semibold text-gray-800">
                    {new Date(account.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>

              <div className="mt-6 flex gap-2">
                <button
                  onClick={() => handleEditAccount(account)}
                  className="flex-1 bg-blue-100 text-blue-600 px-3 py-2 rounded hover:bg-blue-200 text-sm font-semibold"
                >
                  Edit
                </button>
                <button
                  onClick={() => handleDelete(account.id)}
                  className="flex-1 bg-red-100 text-red-600 px-3 py-2 rounded hover:bg-red-200 text-sm font-semibold"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={selectedAccount ? 'Edit Account' : 'Add Account'}
      >
        <AccountForm
          account={selectedAccount}
          studioId={studioId}
          onSubmit={handleSubmit}
          onCancel={() => setIsModalOpen(false)}
        />
      </Modal>
    </div>
  )
}

export default Accounts
